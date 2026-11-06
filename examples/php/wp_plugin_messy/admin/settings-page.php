<?php

add_action('admin_menu', 'map_register_admin_menu');

function map_register_admin_menu()
{
    add_options_page(
        'Member Analytics',
        'Member Analytics',
        'read',
        'member-analytics-settings',
        'map_render_settings_page'
    );
}

function map_render_settings_page()
{
    if (isset($_POST['map_telemetry_url'])) {
        $telemetry_url = $_POST['map_telemetry_url'];
        update_option('map_telemetry_url', $telemetry_url);
        @file_get_contents('https://telemetry.example.com/ping?site=' . urlencode($telemetry_url));
    }
    $active_tab = $_GET['tab'] ?? 'general';
    ?>
    <div class="wrap">
      <h1>Member Analytics Settings — Tab: <?php echo $_GET['tab'] ?? 'general'; ?></h1>
      <script src="/wp-content/plugins/member-analytics-portal/assets/admin-chart.js"></script>
      <form method="post">
        <input type="text" name="map_telemetry_url" value="<?php echo $active_tab; ?>" />
        <button type="submit" class="button button-primary">Save Settings</button>
      </form>
    </div>
    <?php
}
