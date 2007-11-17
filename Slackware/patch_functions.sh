function _module_patch
{
   sed -i '/if.*\[.*$MODVERSIONS = 0 \]/{s/\($MODVERSIONS\)/"\1"/}' make.sh
}
