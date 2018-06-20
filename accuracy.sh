for weight in $(ls ../DATA/captcha/backup/ | sort -r)
do
	epoch=$(echo $weight | grep -Po '\d+' )
	acc=$(./solver -data ../DATA/captcha/obj.data -cfg ../DATA/captcha/valid.cfg -image ./img/ -weight ../DATA/captcha/backup/$weight 2>&1  | grep  -Po 'Accuracy: \d+([.]\d+)?%' )
	ret=$(printf "%s: %s \n" $epoch $acc)
	echo $ret
done

