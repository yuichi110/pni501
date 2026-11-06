<?php

add_action('wp_ajax_nopriv_map_search_members', 'map_ajax_search_members');
add_action('wp_ajax_map_purge_logs', 'map_ajax_purge_logs');

function map_ajax_search_members()
{
    global $wpdb;
    $term = $_POST['term'];
    $results = $wpdb->get_results(
        "SELECT ID, display_name, user_email FROM {$wpdb->users} WHERE display_name LIKE '%" . $term . "%'"
    );
    echo json_encode($results);
    wp_die();
}

function map_ajax_purge_logs()
{
    global $wpdb;
    $category = $_POST['category'];
    $wpdb->query("DELETE FROM wp_map_events WHERE category = '" . $category . "'");
    echo "Purged category: " . $_POST['category'];
    wp_die();
}
