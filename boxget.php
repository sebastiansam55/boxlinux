<?php
if(isset($_GET['identifier'])){
	echo file_get_contents($_GET['identifier']);
	unlink($_GET['identifier']);
}else{
	echo "Something went wrong!";
}


?>