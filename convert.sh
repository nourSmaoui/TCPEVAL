for file in ./*.pdf; do
  name=`basename ${file%.*}`
  echo $name.png
  #echo $file
  convert $file $name.png
done
