<?php
include_once 'includes/db.php';
$conn = get_db_conn();
$cart = isset($_COOKIE['shop_cart']) ? unserialize($_COOKIE['shop_cart']) : [];
$search = isset($_GET['q']) ? $_GET['q'] : '';
$rows = [];
if ($conn && $search !== '') {
    $res = mysqli_query($conn, "SELECT id, title, price FROM products WHERE title LIKE '%" . $search . "%'");
    if ($res) {
        while ($r = mysqli_fetch_assoc($res)) {
            $rows[] = $r;
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head><title>Legacy Shop</title></head>
<body>
  <h1>Welcome to Legacy Shop</h1>
  <p>Search results for: <?= isset($_GET['q']) ? $_GET['q'] : 'all items' ?></p>
  <p>Cart items: <?php echo count(is_array($cart) ? $cart : []); ?></p>
  <?php
  if (isset($_GET['page'])) {
      include $_GET['page'] . '.php';
  }
  ?>
</body>
</html>
