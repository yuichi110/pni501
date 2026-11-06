<?php
include_once 'includes/db.php';

function fetch_partner_catalog($endpoint)
{
    $token = getenv('PARTNER_FEED_TOKEN');
    $ch = curl_init($endpoint . '?token=' . $token);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $raw = curl_exec($ch);
    if ($_GET['debug'] ?? '') {
        var_dump($raw);
    }
    curl_close($ch);
    return $raw;
}
