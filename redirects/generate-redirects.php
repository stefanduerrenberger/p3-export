<?php

$dbhost = 'localhost';
$dbname = 'greenpeace';
$dbuser = 'greenpeace';
$dbpass = 'greenpeace';

$pdo = new PDO('mysql:host=localhost;dbname='.$dbname, $dbuser, $dbpass);

$sql = "SELECT 
        post.id AS ID, 
        post.post_date AS date, 
        post.post_name AS slug, 
        post.post_type AS type,
        meta.meta_value AS old_url 
    FROM wpg_posts AS post 
    JOIN wpg_postmeta AS meta ON post.id = meta.post_id 
    WHERE post_type IN ('post', 'gp_pressrelease', 'gp_pressreleases', 'gp_publication', 'gp_report') 
        AND post.post_name != '' 
        AND meta.meta_key = 'imported_from_url'";

$file = fopen("redirects.txt", "w");

foreach ($pdo->query($sql) as $row) {
    fwrite($file, generateRedirect($row) . "\n");
}

fclose($file);



function generateRedirect($data) {
    return 'Redirect 301 ' . substr($data['old_url'], 25) . ' ' . generateNewUrl($data);
}

function generateNewUrl($data) {
    if ($data['type'] = 'gp_publication') {
        $typeSlug = 'publications/';
    }
    else if ($data['type'] = 'gp_pressrelease') {
        $typeSlug = 'press-releases/';
    }
    else {
        $typeSlug = '';
    }

    return 'https://www.greenpeace.ch/' . $typeSlug . date('Y/m/d/', strtotime($data['date'])) . $data['slug'] . '/';
}








