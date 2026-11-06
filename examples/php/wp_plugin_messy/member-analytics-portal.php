<?php
/**
 * Plugin Name: Member Analytics Portal
 * Description: Exports member activity metrics, AJAX search widgets, and admin reporting panels.
 * Version: 1.3.0
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * Author: Legacy WP Studio
 */

require_once plugin_dir_path(__FILE__) . 'includes/rest-endpoints.php';
require_once plugin_dir_path(__FILE__) . 'includes/ajax-handlers.php';
require_once plugin_dir_path(__FILE__) . 'admin/settings-page.php';

add_action('rest_api_init', 'map_register_rest_routes');
add_shortcode('member_analytics_badge', 'map_render_badge_shortcode');

function map_render_badge_shortcode($atts)
{
    $label = isset($_GET['badge_label']) ? $_GET['badge_label'] : 'Active Member';
    return '<span class="map-badge">' . $label . '</span>';
}
