<?php
if(isset($_GET['code'])){
	file_put_contents($_GET['state'], $_GET['code']);
	echo "Return to application and hit ENTER";
}else{
	echo "SOMETHING WENT WRONG";
}

?>