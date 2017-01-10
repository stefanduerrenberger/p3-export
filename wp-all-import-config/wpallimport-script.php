<?php

/* Put this into the scripts section of WP All Import. It's not imported with the import profile "/"

/*
Old image path: /switzerland/Global/switzerland/photos/toxics/161114_Detox.jpg
New image URL: https://proto2.greenpeace.ch/wp-content/uploads/2016/11/161114_Detox.jpg
*/
add_action('pmxi_saved_post', 'update_images_in_post_content', 10, 3);
function update_images_in_post_content($id) {

	$thepost = get_post($id);

	remove_all_filters('the_content');

	$content = $thepost->post_content;

	$content = preg_replace_callback(
		'/\/switzerland?\/[^ ]+?(?:\.jpg|\.png|\.gif|\.pdf)/', 
		function($matches) {
			for ($i = 0; $i < count($matches); $i++) {
				// set the new upload directory URL
				$newPath = 'http://greenpeace/wp-content/uploads/2017/01/';
				$filename = basename($matches[$i]);

				$filename = sanitize_file_name(urldecode($filename));

				$matches[$i] = $newPath . $filename;
			}

			return $matches[0];
		},
		$content
	);

	$args = array(
		'ID'		=> $id,
		'post_content'	=> $content,
	);

	wp_update_post( $args );
}


?>