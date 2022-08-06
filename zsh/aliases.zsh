alias ls="ls -lh --group-directories-first --color=auto"
alias cam="pkill -f gphoto2; gphoto2 --stdout --capture-movie | ffmpeg -hwaccel nvdec -c:v mjpeg_cuvid -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0"
alias blmod="git status --porcelain | awk '{print \$\2}' | xargs black"
function grepy () {grep "$1" -rn "${2-.}" --include="*.py" --color=always}
