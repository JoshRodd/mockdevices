restart_ps_web
if [[ ${NO_RESTART_INIT} != 0 ]]
then
    restart_init_scripts
fi
make_top_plugins_tar

print_to_log "Installation complete."
exit 0


# NOTE: Don't place any newline characters after the last line below.
__TARFILE_FOLLOWS__
