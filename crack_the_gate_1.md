## 問題
We’re in the middle of an investigation. One of our persons of interest, ctf player, is believed to be hiding sensitive data inside a restricted web portal. We’ve uncovered the email address he uses to log in: ctf-player@picoctf.org. Unfortunately, we don’t know the password, and the usual guessing techniques haven’t worked. But something feels off... it’s almost like the developer left a secret way in. Can you figure it out?


## 回答までの道筋
1. ページソースを確認したら、コメントを発見
2. アルファベットが多く、単語っぽい長さになってるので、ROT13を試す。
3. "X-Dev-Access: yes"ヘッダーをつけたらバイパスできるって書いてた。
4. ヘッダー修正して再送信したらレスポンスにフラグ発見


発見したコメント
```html
 <!-- ABGR: Wnpx - grzcbenel olcnff: hfr urnqre "K-Qri-Npprff: lrf" -->
<!-- Remove before pushing to production! -->  
```

rot13を試した
```
~/repos/ctf_writeups on  main! ⌚ 3:07:42
$ which rot13
rot13: aliased to tr 'A-Za-z' 'N-ZA-Mn-za-m'

~/repos/ctf_writeups on  main! ⌚ 3:07:57
$ echo "ABGR: Wnpx - grzcbenel olcnff: hfr urnqre \"K-Qri-Npprff: lrf\"" | rot13
NOTE: Jack - temporary bypass: use header "X-Dev-Access: yes"
```

ヘッダー修正して再送信した
![devtoolのスクショ](./Screenshot%20from%202026-07-08%2003-27-11.png)
