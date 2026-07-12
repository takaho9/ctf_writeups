---
tags:
  - Web
  - picoCTF
---

# WebDecode

## 問題
- **プラットフォーム / CTF**: picoCTF
- **カテゴリ**: Web
- **難易度**: Easy
- **リンク**: https://learn.cylabacademy.org/library/427?page=1
- **説明**: Do you know how to use the web inspector?

## 使った技術・脆弱性
<!-- 使った脆弱性・手法を箇条書きで -->

## 解答までの道筋
home, about, contactのそれぞれのソースを確認
怪しそうな文字列をaboutで発見
```html
  <section class="about" notify_true="cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMTBmOTM3NmZ9">
   <h1>
    Try inspecting the page!! You might find it there
   </h1>
   <!-- .about-container -->
  </section>
```
英数字だからbase64でdecodeしてみる
```
╰─ base64 -d
cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMTBmOTM3NmZ9
picoCTF{web_succ3ssfully_d3c0ded_10f9376f}
```

## 決め手 / つまずいた点
<!-- 思考プロセスを言語化 -->

## 学んだこと

## 参考
-
