(
dd if="$1" bs=1 skip=26 count=9
dd if=/dev/zero bs=1 count=4
dd if="$1" bs=1 skip=35
) | lzma -dc
