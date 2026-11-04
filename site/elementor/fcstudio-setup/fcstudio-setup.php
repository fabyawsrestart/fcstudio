<?php
/**
 * Plugin Name: FCStudio Setup
 * Description: Configura num clique os 7 breakpoints, cores e fontes globais, o Menu principal e a Home estática da FCStudio. Depois de usar, desative e apague.
 * Version: 1.0.0
 * Requires Plugins: elementor
 * Author: FCStudio
 */

if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'admin_menu', function () {
	add_management_page( 'FCStudio Setup', 'FCStudio Setup', 'manage_options', 'fcstudio-setup', 'fcstudio_setup_page' );
} );

// Link "Abrir" na lista de plugins
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
		<li>Cria o "Menu principal" com os 5 links (se ainda não existir).</li>
		<li>Cria ou atualiza a página <strong>Home</strong> com o layout Elementor Canvas e define como página inicial estática.</li>
	</ul><p><em>Atenção: se já existir uma página chamada Home, o conteúdo dela será substituído.</em></p>
	<form method="post">';
	wp_nonce_field( 'fcstudio_setup' );
	echo '<p><button class="button button-primary button-hero" name="fcstudio_run" value="1">Configurar agora</button></p></form></div>';
}

function fcstudio_setup_run() {
	$log = [];
	if ( ! did_action( 'elementor/loaded' ) ) return [ 'Elementor não está ativo. Ative o Elementor e tente de novo.' ];
	$E   = \Elementor\Plugin::$instance;
	$dir = plugin_dir_path( __FILE__ );
	$kitS = json_decode( file_get_contents( $dir . 'kit-settings.json' ), true );
	$tpl  = json_decode( file_get_contents( $dir . 'fcstudio-home.json' ), true );

	// 1. Kit: breakpoints, largura útil, cores e fontes (mescla com o que já existe)
	$kit = $E->kits_manager->get_active_kit();
	if ( ! $kit || ! $kit->get_id() ) {
		$E->kits_manager->create_default();
		$kit = $E->kits_manager->get_active_kit();
	}
	$current = (array) $kit->get_meta( '_elementor_page_settings' );
	$kit->save( [ 'settings' => array_merge( $current, $kitS ) ] );
	\Elementor\Core\Breakpoints\Manager::compile_stylesheet_templates();
	$saved = get_post_meta( $kit->get_id(), '_elementor_page_settings', true );
	$log[] = 'Breakpoints ativos: ' . count( (array) ( $saved['active_breakpoints'] ?? [] ) ) . ' adicionais + desktop = ' . ( 1 + count( (array) ( $saved['active_breakpoints'] ?? [] ) ) ) . ' no total. Celular retrato até ' . ( $saved['viewport_mobile'] ?? '?' ) . 'px.';

	// 2. Menu principal
	$menu = wp_get_nav_menu_object( 'menu-principal' ) ?: wp_get_nav_menu_object( 'Menu principal' );
	if ( ! $menu ) {
		$mid = wp_create_nav_menu( 'Menu principal' );
		foreach ( [ [ 'Serviços', '#servicos' ], [ 'Como funciona', '#como-funciona' ], [ 'Planos', '#planos' ], [ 'Portfólio', '#portfolio' ], [ 'Contato', '#contato' ] ] as $it ) {
			wp_update_nav_menu_item( $mid, 0, [ 'menu-item-title' => $it[0], 'menu-item-url' => $it[1], 'menu-item-status' => 'publish', 'menu-item-type' => 'custom' ] );
		}
		$log[] = 'Menu principal criado.';
	} else {
		$log[] = 'Menu principal já existia, mantido.';
	}

	// 3. Página Home
	$page = get_page_by_path( 'home' );
	if ( ! $page ) {
		foreach ( get_posts( [ 'post_type' => 'page', 'title' => 'Home', 'post_status' => 'any', 'numberposts' => 1 ] ) as $p ) $page = $p;
	}
	$pid = $page ? $page->ID : wp_insert_post( [ 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Home', 'post_name' => 'home' ] );
	wp_update_post( [ 'ID' => $pid, 'post_status' => 'publish' ] );
	update_post_meta( $pid, '_elementor_edit_mode', 'builder' );
	update_post_meta( $pid, '_elementor_template_type', 'wp-page' );
	update_post_meta( $pid, '_wp_page_template', 'elementor_canvas' );
	$doc = $E->documents->get( $pid, false );
	$doc->save( [ 'elements' => $tpl['content'], 'settings' => [ 'template' => 'elementor_canvas', 'hide_title' => 'yes' ] ] );
	$log[] = 'Página Home ' . ( $page ? 'atualizada' : 'criada' ) . ' (ID ' . $pid . ') com layout Elementor Canvas.';

	// 4. Página inicial estática
	update_option( 'show_on_front', 'page' );
	update_option( 'page_on_front', $pid );
	$log[] = 'Home definida como página inicial estática.';

	// 5. Usar as cores e fontes do kit, não as do tema
	update_option( 'elementor_disable_color_schemes', 'yes' );
	update_option( 'elementor_disable_typography_schemes', 'yes' );

	$E->files_manager->clear_cache();
	$log[] = 'Cache do Elementor limpo.';
	return $log;
}
