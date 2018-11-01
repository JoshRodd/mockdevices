#concatenate bash-common.sh here#
extract_customer_files ()
{
  PATH_PREFIX=${1}
  extract_ps_files ${PATH_PREFIX}
  print_to_log "Copying web page files."
  cp -r ${CUST_WWW_DIR}/* ${PATH_PREFIX}${PS_WWW_DIR} &> /dev/null
  if [ -d ${PS_INIT_DIR} ]; then
  	print_to_log "Copying init scripts files."
  	if [ ! -d ${PATH_PREFIX}${OS_INIT_DIR} ]
  	then
  	  mkdir -p ${PATH_PREFIX}${OS_INIT_DIR}
  	fi
  	cp -r ${PS_INIT_DIR}/* ${PATH_PREFIX}${OS_INIT_DIR} &> /dev/null
  fi

  if [ -d ${PS_LOCAL_ST_DIR} ]; then
    chown ${ST_USER}:${ST_USER} ${PS_LOCAL_ST_DIR}/* -R
    chmod 0770 ${PS_LOCAL_ST_DIR}/* -R
  	cp -ra ${PS_LOCAL_ST_DIR}/* ${PATH_PREFIX}${OS_LOCAL_ST_DIR} &> /dev/null
  fi

}

set_customer_permissions ()
{
  DEST_PREFIX=${1}
  print_to_log "Setting permissions."
  if [[ ${TOMCAT_USER_EXISTS} == 0 ]]
  then
	if [[ ${APACHE_GROUP_EXISTS} == 0 ]]
    then
      CHOWN_STRING=${TOMCAT_USER}:${APACHE_GROUP}
    else
      CHOWN_STRING=${TOMCAT_USER}
    fi
  else
    print_to_log "User ${TOMCAT_USER} does not exist, setting owner to current user (${ORIGINAL_USER})."
    CHOWN_STRING=${ORIGINAL_USER}
  fi

  for folder in ${PS_INSTALL_DIR} ${PS_LOG_DIR} ${PS_PID_DIR} ${PS_WWW_DIR}
  do
    if [[ -d ${folder} ]]
    then
		chown ${CHOWN_STRING} ${folder} -R
    fi
  done


  chmod 0666 ${PS_LOG_DIR} -R
  chmod 0777 ${PS_LOG_DIR}
  chmod 0755 ${DEST_PREFIX}${PS_INSTALL_DIR}
  chmod 0664 ${DEST_PREFIX}${PS_INSTALL_DIR}/conf -R
  chmod 0775 ${DEST_PREFIX}${PS_INSTALL_DIR}/conf
  chmod 0660 ${DEST_PREFIX}${PS_INSTALL_DIR}/templates -R
  chmod 0770 ${DEST_PREFIX}${PS_INSTALL_DIR}/templates
  chmod 0770 ${DEST_PREFIX}${PS_INSTALL_DIR}/bin -R
  chmod 0770 ${DEST_PREFIX}${PS_WWW_DIR}/ -R

  if [[ -d ${ST_DIR} ]]
  then
      chown ${ST_USER}:${ST_USER} ${ST_DIR} -R
      chmod 0755 ${ST_DIR} -R
  fi
}


OPTS=$(getopt -o hx: --long help,extract-only:,no-restart-init -n "${0}" -- "$@")
RESTART_INIT=1
if [ $? != 0 ]
then
    echo "Could not parse arguments for ${0}"
    exit 1
fi
eval set -- "$OPTS"

while true
do
    case "${1}" in
        -h | --help) print_help
            shift
        ;;
        -x | --extract-only) EXTRACT_DEST_PREFIX="${2}"
            shift 2
            print_to_log "Extracting files only to ${EXTRACT_DEST_PREFIX}${PS_INSTALL_DIR}."
            detect_script_package_path_and_size
            check_hash
            extract_ps_files ${EXTRACT_DEST_PREFIX}
            set_ps_permissions ${EXTRACT_DEST_PREFIX}
            exit 0
        ;;
        --no-restart-init) NO_RESTART_INIT=0
            shift
        ;;
        --) shift
            break
        ;;
        * ) break
        ;;
    esac
done


create_text_box "${TUFIN_PS_TITLE}" "${TITLE}"
validate_root

detect_script_package_path_and_size
check_hash
extract_customer_files
set_customer_permissions
