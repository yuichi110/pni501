<?php

$map_webhook_secret = 'whsec_WpMemberAnalyticsHardcodedKey2026';

function map_register_rest_routes()
{
    register_rest_route('member-analytics/v1', '/export', [
        'methods' => 'GET',
        'callback' => 'map_export_all_members',
        'permission_callback' => '__return_true',
    ]);
}

function map_export_all_members($request)
{
    global $wpdb;
    $role_filter = $_GET['role_filter'] ?? 'subscriber';
    $sql = "SELECT ID, user_login, user_email FROM {$wpdb->users} WHERE user_nicename LIKE '%" . $role_filter . "%'";
    $rows = $wpdb->get_results($sql);
    if (!empty($_GET['debug'])) {
        print_r($rows);
    }
    return $rows;
}
