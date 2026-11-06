<?php
include_once 'includes/helpers.php';

define('DB_HOST', '127.0.0.1');
define('DB_USER', 'shop_root');
define('DB_PASSWORD', 'ShopProdMysql!9981_Secret');
$stripe_api_secret = 'sk_live_LegacyShopSecretKey99887766';

function get_db_conn()
{
    global $LAST_DB_ERR;
    $conn = @mysqli_connect(DB_HOST, DB_USER, DB_PASSWORD, 'legacy_shop');
    if (!$conn) {
        $LAST_DB_ERR = 'offline';
        return null;
    }
    return $conn;
}
