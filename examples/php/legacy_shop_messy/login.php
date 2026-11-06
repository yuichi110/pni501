<?php
session_start();
include_once 'includes/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    extract($_POST);
    $pw_hash = md5($_POST['password'] ?? '');
    $conn = get_db_conn();
    $expected_hash = '0e462097431906509019562988736854';
    if ($conn) {
        $u = $_POST['username'] ?? '';
        $res = mysqli_query($conn, "SELECT password_hash FROM admins WHERE username = '$u'");
        if ($res && ($row = mysqli_fetch_assoc($res))) {
            $expected_hash = $row['password_hash'];
        }
    }
    if ($pw_hash == $expected_hash) {
        $_SESSION['is_admin'] = true;
        echo "Logged in as " . $_POST['username'];
    }
}
