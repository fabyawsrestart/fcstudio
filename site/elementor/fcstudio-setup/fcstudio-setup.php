<?php
/**
 * Plugin Name: FCStudio Setup
 * Description: Configura num clique os 7 breakpoints, cores e fontes globais, cabeçalho e rodapé do site, o Menu principal e as páginas Home, Serviços, Planos, Portfólio e Contato. Depois de usar, desative e apague.
 * Version: 1.2.0
 * Requires Plugins: elementor
 * Author: FCStudio
 */

if ( ! defined( 'ABSPATH' ) ) exit;

const FCSTUDIO_PAGES = [
	'home'      => 'Home',
	'servicos'  => 'Serviços',
	'planos'    => 'Planos',
	'portfolio' => 'Portfólio',
	'contato'   => 'Contato',
];

add_action( 'admin_menu', function () {
	add_management_page( 'FCStudio Setup', 'FCStudio Setup', 'manage_options', 'fcstudio-setup', 'fcstudio_setup_page' );
} );

add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), function ( $links ) {
	array_unshift( $links, '<a href="' . admin_url( 'tools.php?page=fcstudio-setup' ) . '">Abrir</a>' );
	return $links;
} );

function fcstudio_setup_page() {
	if ( ! current_user_can( 'manage_options' ) ) return;
	echo '<div class="wrap"><h1>FCStudio Setup</h1>';

	if ( isset( $_POST['fcstudio_run'] ) && check_admin_referer( 'fcstudio_setup' ) ) {
		$log = fcstudio_setup_run();
		echo '<div class="notice notice-success"><p><strong>Pronto.</strong></p><ul style="list-style:disc;margin-left:20px">';
		foreach ( $log as $l ) echo '<li>' . esc_html( $l ) . '</li>';
		echo '</ul></div><p><a class="button button-primary" href="' . esc_url( home_url( '/' ) ) . '" target="_blank">Ver o site</a> ';
		echo '<a class="button" href="' . esc_url( admin_url( 'plugins.php' ) ) . '">Desativar e apagar este plugin</a></p></div>';
		return;
	}

	echo '<p>Este botão faz, de uma vez:</p><ul style="list-style:disc;margin-left:20px">
		<li>Ativa os 7 breakpoints (celular retrato até 575px, paisagem até 880px, tablet retrato 1024, tablet paisagem 1200, laptop 1366, widescreen 2400).</li>
		<li>Aplica a largura útil (1140px, 1320px no widescreen), as cores e as tipografias globais.</li>
		<li>Cria o <strong>Cabeçalho</strong> e o <strong>Rodapé</strong> no Theme Builder, valendo para o site todo.</li>
		<li>Cria ou atualiza as páginas <strong>Home, Serviços, Planos, Portfólio e Contato</strong> e define a Home como página inicial estática.</li>
		<li>Monta o "Menu principal" apontando para as páginas.</li>
	</ul><p><em>Atenção: páginas com esses nomes que já existirem terão o conteúdo substituído.</em></p>
	<form method="post">';
	wp_nonce_field( 'fcstudio_setup' );
	echo '<p><button class="button button-primary button-hero" name="fcstudio_run" value="1">Configurar agora</button></p></form></div>';
}

/** Envia as imagens de assets/ para a Biblioteca de mídia (uma vez só) e devolve [token => [id, url]]. */
function fcstudio_images() {
	require_once ABSPATH . 'wp-admin/includes/image.php';
	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';
	$out = [];
	foreach ( glob( plugin_dir_path( __FILE__ ) . 'assets/*.{jpg,png,webp}', GLOB_BRACE ) as $file ) {
		$name  = basename( $file );
		$token = preg_replace( '/^portfolio-|\.(jpg|png|webp)$/', '', $name );
		$found = get_posts( [ 'post_type' => 'attachment', 'meta_key' => '_fcstudio_asset', 'meta_value' => $name, 'numberposts' => 1, 'post_status' => 'any' ] );
		if ( $found ) {
			$id = $found[0]->ID;
		} else {
			$tmp = wp_tempnam( $name );
			copy( $file, $tmp );
			$id = media_handle_sideload( [ 'name' => $name, 'tmp_name' => $tmp ], 0 );
			if ( is_wp_error( $id ) ) continue;
			update_post_meta( $id, '_fcstudio_asset', $name );
		}
		$out[ $token ] = [ $id, wp_get_attachment_url( $id ) ];
	}
	return $out;
}

/** Lê um JSON trocando os links "fc://slug" e as imagens "fc-img://token" pelos endereços reais. */
function fcstudio_load( $file, $urls, $imgs = [] ) {
	$raw = file_get_contents( plugin_dir_path( __FILE__ ) . $file );
	foreach ( $imgs as $token => $img ) {
		$raw = str_replace( [ '"fc-imgid://' . $token . '"', 'fc-img://' . $token ], [ (string) (int) $img[0], str_replace( '/', '\\/', $img[1] ) ], $raw );
	}
	foreach ( $urls as $slug => $url ) {
		$raw = str_replace( 'fc://' . $slug, str_replace( '/', '\\/', $url ), $raw );
	}
	return json_decode( $raw, true );
}

function fcstudio_find_page( $slug, $title ) {
	$page = get_page_by_path( $slug );
	if ( $page ) return $page;
	foreach ( get_posts( [ 'post_type' => 'page', 'title' => $title, 'post_status' => 'any', 'numberposts' => 1 ] ) as $p ) return $p;
	return null;
}

function fcstudio_setup_run() {
	$log = [];
	if ( ! did_action( 'elementor/loaded' ) ) return [ 'Elementor não está ativo. Ative o Elementor e tente de novo.' ];
	$E   = \Elementor\Plugin::$instance;
	$pro = defined( 'ELEMENTOR_PRO_VERSION' ) && class_exists( '\ElementorPro\Modules\ThemeBuilder\Module' );

	// 1. Kit: breakpoints, largura útil, cores e fontes
	$kitS = fcstudio_load( 'kit-settings.json', [] );
	$kit  = $E->kits_manager->get_active_kit();
	if ( ! $kit || ! $kit->get_id() ) {
		$E->kits_manager->create_default();
		$kit = $E->kits_manager->get_active_kit();
	}
	$current = (array) $kit->get_meta( '_elementor_page_settings' );
	$kit->save( [ 'settings' => array_merge( $current, $kitS ) ] );
	\Elementor\Core\Breakpoints\Manager::compile_stylesheet_templates();
	$saved = get_post_meta( $kit->get_id(), '_elementor_page_settings', true );
	$n     = count( (array) ( $saved['active_breakpoints'] ?? [] ) );
	$log[] = 'Breakpoints: ' . ( $n + 1 ) . ' ativos (desktop + ' . $n . '). Celular retrato até ' . ( $saved['viewport_mobile'] ?? '?' ) . 'px.';

	// 2. Cria as páginas primeiro, para saber os links
	$ids = [];
	foreach ( FCSTUDIO_PAGES as $slug => $title ) {
		$page = fcstudio_find_page( $slug, $title );
		$ids[ $slug ] = $page ? $page->ID : wp_insert_post( [ 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => $title, 'post_name' => $slug ] );
		wp_update_post( [ 'ID' => $ids[ $slug ], 'post_status' => 'publish' ] );
	}
	update_option( 'show_on_front', 'page' );
	update_option( 'page_on_front', $ids['home'] );
	$urls = [];
	foreach ( $ids as $slug => $id ) $urls[ $slug ] = get_permalink( $id );
	$urls['home'] = home_url( '/' );

	// 3. Conteúdo das páginas
	$imgs = fcstudio_images();
	foreach ( FCSTUDIO_PAGES as $slug => $title ) {
		$tpl = fcstudio_load( 'paginas/' . $slug . '.json', $urls, $imgs );
		$pid = $ids[ $slug ];
		// Sem o Pro (sem cabeçalho/rodapé globais) a página precisaria do Canvas; com o Pro usa "Elementor Largura total"
		$template = $pro ? 'elementor_header_footer' : 'elementor_canvas';
		update_post_meta( $pid, '_elementor_edit_mode', 'builder' );
		update_post_meta( $pid, '_elementor_template_type', 'wp-page' );
		update_post_meta( $pid, '_wp_page_template', $template );
		$E->documents->get( $pid, false )->save( [ 'elements' => $tpl['content'], 'settings' => [ 'template' => $template, 'hide_title' => 'yes' ] ] );
	}
	$log[] = 'Páginas criadas/atualizadas: ' . implode( ', ', FCSTUDIO_PAGES ) . '. Home definida como página inicial estática.';

	// 4. Cabeçalho e rodapé globais (Theme Builder do Pro)
	if ( $pro ) {
		foreach ( [ 'cabecalho' => [ 'header', 'FCStudio Cabeçalho' ], 'rodape' => [ 'footer', 'FCStudio Rodapé' ] ] as $file => [ $type, $title ] ) {
			$tpl   = fcstudio_load( 'paginas/' . $file . '.json', $urls, $imgs );
			$found = get_posts( [ 'post_type' => 'elementor_library', 'title' => $title, 'post_status' => 'any', 'numberposts' => 1 ] );
			if ( $found ) {
				$tid = $found[0]->ID;
			} else {
				$doc = $E->documents->create( $type, [ 'post_title' => $title, 'post_status' => 'publish' ] );
				$tid = $doc->get_main_id();
			}
			wp_update_post( [ 'ID' => $tid, 'post_status' => 'publish' ] );
			$E->documents->get( $tid, false )->save( [ 'elements' => $tpl['content'] ] );
			update_post_meta( $tid, '_elementor_conditions', [ 'include/general' ] );
		}
		\ElementorPro\Modules\ThemeBuilder\Module::instance()->get_conditions_manager()->get_cache()->regenerate();
		$log[] = 'Cabeçalho e rodapé criados no Theme Builder, valendo para o site todo.';
	} else {
		$log[] = 'Pro Elements não está ativo: cabeçalho e rodapé globais NÃO foram criados. Ative o Pro Elements e rode de novo.';
	}

	// 5. Menu principal apontando para as páginas
	$menu = wp_get_nav_menu_object( 'menu-principal' ) ?: wp_get_nav_menu_object( 'Menu principal' );
	$mid  = $menu ? $menu->term_id : wp_create_nav_menu( 'Menu principal' );
	foreach ( (array) wp_get_nav_menu_items( $mid, [ 'post_status' => 'any' ] ) as $item ) wp_delete_post( $item->ID, true );
	foreach ( [ 'servicos', 'planos', 'portfolio', 'contato' ] as $slug ) {
		wp_update_nav_menu_item( $mid, 0, [ 'menu-item-title' => FCSTUDIO_PAGES[ $slug ], 'menu-item-object' => 'page', 'menu-item-object-id' => $ids[ $slug ],
			'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ] );
	}
	if ( 'menu-principal' !== wp_get_nav_menu_object( $mid )->slug ) wp_update_term( $mid, 'nav_menu', [ 'slug' => 'menu-principal' ] );
	$log[] = 'Menu principal: Serviços, Planos, Portfólio e Contato.';

	update_option( 'elementor_disable_color_schemes', 'yes' );
	update_option( 'elementor_disable_typography_schemes', 'yes' );
	$E->files_manager->clear_cache();
	$log[] = 'Cache do Elementor limpo.';
	return $log;
}
