mockdevices_check_install.sh --install
if [ $? -ne 0 ]; then
	printf "Package installation failed.\n"
	exit 1
fi
