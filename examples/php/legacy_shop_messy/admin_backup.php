<?php
include_once 'includes/db.php';

if (isset($_POST['backup_dir'])) {
    $target = $_POST['backup_dir'];
    $output = shell_exec("tar -czf /tmp/shop_backup.tar.gz " . $target);
    echo "<pre>Backup completed:\n" . $output . "</pre>";
}
?>
<form method="post">
  <input type="text" name="backup_dir" value="/var/www/html/uploads" />
  <button type="submit">Run Backup</button>
</form>
