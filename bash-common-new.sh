DEFAULT_LOG_LEVEL="WARNING"
LOG_DOMAINS="common helpers reports requests mail sql third_party xml web"
PYTHON_MAJOR_VERSION="3.4"
PYTHON_MINOR_VERSION="2"
TOMCAT_USER="tomcat"
APACHE_GROUP="apache"
ST_USER="st"
TARGET_MD5SUM="__MD5SUM_PLACE_HOLDER__"
TARGET_SHA256SUM="__SHA256SUM_PLACE_HOLDER__"
LIGHT_FLAG="__LIGHT_FLAG_PLACEHOLDER__"
TITLE="__TITLE_PLACE_HOLDER__"
PS_LIB_VERSION=__PS_LIB_VERSION_PLACE_HOLDER__
EASY_INSTALL_STRING="import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)"

PS_INSTALL_DIR="/"
WEB_ENABLED_FILE="${PS_INSTALL_DIR}/conf/WEB_ENABLED"
INSTALL_LOG="${PS_INSTALL_DIR}/install.log"
PS_LOG_DIR="/var/log/ps"
PS_DB_DIR="/var/cache/ps/db"

ORACLE_HOME_PATH="/usr/lib/oracle/11.2/client64"
ORACLE_CLIENT_LIB_PATH="${ORACLE_HOME_PATH}/lib/"
ORACLE_PROFILE_CONFIG_FILE="/etc/profile.d/oracle.sh"

PS_PID_DIR="/var/run/ps"
WWW_DIR="${PS_INSTALL_DIR}/resource/other/www"
CUST_WWW_DIR="${PS_INSTALL_DIR}/www"
PS_WWW_DIR="/var/wwwps/"
PS_INIT_DIR="${PS_INSTALL_DIR}/init"
TOP_PLUGINS_DIR="${PS_INSTALL_DIR}/top"
OS_INIT_DIR="/etc/init.d"
TAR="/bin/tar"
PS_FOLDERS=(${PS_INSTALL_DIR} ${PS_LOG_DIR} ${PS_PID_DIR} ${PS_WWW_DIR} ${PS_DB_DIR})
ST_DIR="${PS_INSTALL_DIR}/st"
PS_LOCAL_ST_DIR="${PS_INSTALL_DIR}/local_st"
OS_LOCAL_ST_DIR="/usr/local/st"

shopt -s extglob
ORIGINAL_USER=$(logname)
RPM_EXISTS=$(which rpm >> ${INSTALL_LOG} 2>&1;echo $?)
PS_PYTHON_EXISTS=$(${PS_INSTALL_DIR}/python/bin/python3 -V >> ${INSTALL_LOG} 2>&1;echo $?)
CHKCONFIG_EXISTS=$(which chkconfig >> ${INSTALL_LOG} 2>&1;echo $?)
TOMCAT_USER_EXISTS=$(id ${TOMCAT_USER} >> ${INSTALL_LOG} 2>&1;echo $?)
APACHE_GROUP_EXISTS=$(id ${APACHE_GROUP} >> ${INSTALL_LOG} 2>&1;echo $?)
SUDO_EXISTS=$(which sudo >> ${INSTALL_LOG} 2>&1;echo $?)
SHA256SUM_EXISTS=$(which sha256sum >> ${INSTALL_LOG} 2>&1;echo $?)
WEB_ENABLED=$(test -e ${WEB_ENABLED_FILE};echo $?)

get_current_installed_version() {
    if [ -f ${PS_VERSION_FILE} ]
    then
        CURRENT_PS_LIB_VERSION=$(awk '{print $2}' ${PS_VERSION_FILE})
    else
        CURRENT_PS_LIB_VERSION=0
    fi
}

detect_script_package_path_and_size()
{
    SOURCE0="$B_SOURCE"
#    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "${B_SOURCE}" ]; do
        INSTALL_SCRIPT_DIR="$( cd -P "$( dirname "${B_SOURCE}" )" && pwd )"
        B_SOURCE="$(readlink --canonicalize --no-newline "${B_SOURCE}")"
        [[ ${B_SOURCE} != /* ]] && B_SOURCE="${INSTALL_SCRIPT_DIR}/${B_SOURCE}"
    done
    INSTALL_SCRIPT_DIR="$( cd -P "$( dirname "${B_SOURCE}" )" && pwd )"

    #remember our file name
    INSTALL_SCRIPT_FILE=${INSTALL_SCRIPT_DIR}/$(basename "${SOURCE0##*/}")

    SKIP=$(awk '/^__TARFILE_FOLLOWS__/ { print NR + 1; exit 0; }' "${INSTALL_SCRIPT_FILE}")
}


check_hash(){
    if [[ ${SHA256SUM_EXISTS} == 0 ]]
    then
        check_sha256sum
    else
        check_md5sum
    fi
}

check_md5sum()
{
    FILE_MD5SUM=$(tail -n +${SKIP} "${INSTALL_SCRIPT_FILE}" | openssl base64 -d | openssl dgst -md5 -binary | xxd -c 32 -p | awk '{print $1}')

    if [ "${TARGET_MD5SUM}" != "${FILE_MD5SUM}" ]
    then
        print_to_log "MD5sum of embedded archive is corrupt, exiting."
        exit 1
    else
        print_to_log "MD5sum of embedded archive is valid, continuing."
    fi
}

check_sha256sum()
{
    FILE_SHA256SUM=$(tail -n +${SKIP} "${INSTALL_SCRIPT_FILE}" | openssl base64 -d | openssl dgst -sha256 -binary | xxd -c 32 -p | awk '{print $1}')

    if [ "${TARGET_SHA256SUM}" != "${FILE_SHA256SUM}" ]
    then
        print_to_log "SHA256sum of embedded archive is corrupt, exiting."
        exit 1
    else
        :
    fi
}


print_to_log()
{
    echo "$@" | tee -a ${INSTALL_LOG}
}


extract_ps_files ()
{
  PATH_PREFIX=${1}
  if [ ! -d "${PATH_PREFIX}${PS_INSTALL_DIR}" ]; then
	  print_to_log "Creating folder ${PATH_PREFIX}${PS_INSTALL_DIR}"
	  mkdir -p ${PATH_PREFIX}${PS_INSTALL_DIR}
  fi

  print_to_log "Extracting files into ${PATH_PREFIX}${PS_INSTALL_DIR}"
  tail -n +${SKIP} "${INSTALL_SCRIPT_FILE}" | openssl base64 -d | tar mxfj - -C ${PATH_PREFIX}${PS_INSTALL_DIR} &> /dev/null
}

create_folders()
{
    for folder in "${PS_FOLDERS[@]}"
    do
        if [ ! -d "${folder}" ]; then
            mkdir -p "${folder}"
        fi
    done
}

function create_text_box()
{
  local s=("$@") b w
  for l in "${s[@]}"; do
    ((w<${#l})) && { b="$l"; w="${#l}"; }
  done
  tput setaf 4
  echo -e " #${b//?/#}#\n# ${b//?/ } #"
  for line in "${s[@]}"; do
    printf '# %s%*s%s #\n' "$(tput setaf 3)" "-$w" "$line" "$(tput setaf 4)"
  done
  echo "# ${b//?/ } #
 #${b//?/#}#"
  tput sgr 0
}

validate_root(){
    # Make sure only root can run our script
    if [[ ${EUID} -ne 0 ]]; then
        cat <<EOT
This script must be run as root.
Try this command:

	sudo $B_SOURCE
EOT
        exit 1
    fi
}

print_help ()
{
	cat <<EOT
Usage: $B_SOURCE [-x EXTRACT_DIR]

The -x option will extract to a specific directory but not run the installer.
EOT
exit 0
}
extract_package_files ()
{
  PATH_PREFIX="${1}"
  extract_ps_files "${PATH_PREFIX}"
}

OPTS=$(getopt -o fhx: --long force,help,extract-only:,uninstall -n "${B_SOURCE}" -- "$@")
RESTART_INIT=1
FORCE=""
if [ $? != 0 ]
then
    echo "Could not parse arguments for ${B_SOURCE}"
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
            extract_ps_files "${EXTRACT_DEST_PREFIX}"
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

mockdevices_check_install.sh --install
if [ $? -ne 0 ]; then
	printf "Package installation failed.\n"
	exit 1
fi
exit 0
