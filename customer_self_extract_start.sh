#concatenate bash-common.sh here#
extract_package_files ()
{
  PATH_PREFIX=${1}
  extract_ps_files ${PATH_PREFIX}
}

OPTS=$(getopt -o fhx: --long force,help,extract-only:,uninstall -n "${0}" -- "$@")
RESTART_INIT=1
FORCE=""
if [ $? != 0 ]
then
    echo "Could not parse arguments for ${0}"
    exit 1
fi
eval set -- "$OPTS"

while true
do
    case "${1}" in
        -f | --force) shift
            FORCE="--force"
        ;;
        -h | --help) print_help
            shift
        ;;
        -x | --extract-only) EXTRACT_DEST_PREFIX="${2}"
            shift 2
            printf "Extracting files only to ${EXTRACT_DEST_PREFIX}${PS_INSTALL_DIR}.\n"
            detect_script_package_path_and_size
            check_hash
            extract_ps_files ${EXTRACT_DEST_PREFIX}
            exit 0
        ;;
	--uninstall) shift
            detect_script_package_path_and_size
            check_hash
            extract_ps_files
            mockdevices_check_install.sh --uninstall $FORCE
            exit
        ;;
        --) shift
            break
        ;;
        * ) break
        ;;
    esac
done


validate_root

detect_script_package_path_and_size
check_hash
extract_package_files
