for file in ./*.pdf; do
  name=`basename ${file%.*}`
  echo $name.png
  convert $file $name.png
done
