<?php
include_once 'includes/db.php';
$conn = get_db_conn();
$cat = $_GET['cat'] ?? 'featured';
if ($conn) {
    $sql = "SELECT * FROM products WHERE category = '" . $cat . "' ORDER BY id DESC";
    $result = mysqli_query($conn, $sql);
    if (!$result) {
        die("Database query failed: " . mysqli_error($conn));
    }
}
?>
<div class="product-banner">
  <?php echo $_GET['promo_html'] ?? 'Special Sale'; ?>
</div>
