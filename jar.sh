### SDK JAR Fetcher ###
fetch_android_jar() {
  local api=$1
  local dest="$SDK_HOME/android-$api.jar"
  local mirrors=(
    "https://dl.google.com/android/repository/platforms/android-$api/android.jar"
    "https://androidx.dev/snapshots/platforms/android-$api/android.jar"
    "https://raw.githubusercontent.com/Sable/android-platforms/master/android-$api/android.jar"
  )

  if [ -f "$dest" ]; then
    echo -e "${GREEN}✔ Android API $api JAR already present${NC}"
    return 0
  fi

  for url in "${mirrors[@]}"; do
    echo -e "${BLUE}⬇ Trying: $url${NC}"
    if wget --continue -q -O "$dest" "$url"; then
      echo -e "${GREEN}✔ Downloaded android-$api.jar${NC}"
      return 0
    fi
  done

  echo -e "${YELLOW}⚠ Failed to download API $api. You may import manually.${NC}"
  return 1
}

### Offline Import Mode ###
if [[ "$1" == "--import-jars" && -d "$2" ]]; then
  echo -e "${BLUE}📂 Importing local JARs from $2${NC}"
  mkdir -p "$SDK_HOME"
  cp -v "$2"/android-*.jar "$SDK_HOME/" || true
fi

### Download All Required APIs ###
for api in {28..34}; do
  fetch_android_jar $api || true
done
