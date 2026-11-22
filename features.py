"""特集ページ（季節・イベントごとのまとめ）。各ジャンルの単価上位3件を summary.json の top3 から並べる。
months に今月が入っている特集をトップで先に出す。ジャンルの中身は毎朝の更新でそのまま入れ替わる。"""
import html
import json

FEATURES = [
    {
        "slug": "tokushu-osouji",
        "short": "大掃除",
        "title": "大掃除の洗剤・消耗品 まとめ買い最安ガイド",
        "desc": "オキシクリーン・除菌シート・キッチンペーパー・ゴミ袋など、大掃除で使う消耗品を楽天市場の1回あたり単価で比較。毎朝更新の最安上位3件をまとめました。",
        "lead": "大掃除はオキシクリーンや除菌シート、ゴミ袋をたくさん使います。量が多いぶん、1回あたりの単価で選ぶと差がはっきり出ます。毎日自動で、楽天市場の最安上位3件へ入れ替わります。",
        "months": [11, 12],
        "guide": [
            ("使う量の目安", "オキシクリーンのつけ置きは、40〜60℃のお湯4Lに付属スプーン1杯が目安です（商品の表示を確認してください）。換気扇・五徳・浴室の小物をまとめて漬けると、家1軒の大掃除で500g〜1kgほど使います。ゴミ袋は不用品の処分で普段の2〜3倍、キッチンペーパーや除菌シートも普段の倍くらい減ります。"),
            ("始める順番", "上から下へ（照明・換気扇→棚→床）、奥から手前へ進めると、落ちたホコリをもう一度拭かずにすみます。油汚れは気温が高いほうがゆるむので、寒くなりきる前の11月〜12月上旬に台所から始めるのがおすすめです。"),
            ("注意すること", "酸素系漂白剤（オキシクリーン）は、塩素系漂白剤と同時に使わないでください。アルミ・銅・木製品・漆器・ウールや絹は変色や傷みの原因になるので、つけ置きに向きません。作業中はゴム手袋をつけ、換気をしてください。"),
        ],
        "faq": [
            ("オキシクリーンと過炭酸ナトリウムは何が違う？", "主成分はどちらも過炭酸ナトリウムです。日本で売られている版は界面活性剤なし、アメリカ版（コストコなど）は界面活性剤入りで泡立ちます。ブランドにこだわらなければ、過炭酸ナトリウムの大袋がいちばん安く買えます。"),
            ("大掃除の洗剤はどれくらい買っておけばいい？", "オキシクリーンなら1.5kg〜2kg、ゴミ袋は45Lを50枚、除菌シートは詰め替え2〜3個が一般的な家庭の目安です。使い切れなくても、どれも普段の掃除や洗濯で使えるので無駄になりにくい消耗品です。"),
        ],
        "items": [
            ("oxygen-bleach", "換気扇・五徳のつけ置き、浴室の小物に。お湯で溶かすと効きやすい"),
            ("disinfect-wipes", "ドアノブ・スイッチ・冷蔵庫の取っ手の拭き掃除に"),
            ("kitchen-paper", "油汚れの拭き取りに。大掃除では普段の倍くらい使う"),
            ("garbage-bag-45l", "不用品の処分で一気に減る。年末の収集日に合わせて多めに"),
            ("dish-soap-refill", "つけ置き洗いに大量に使うなら詰め替えの大容量が得"),
            ("dishwasher-tablet", "庫内の掃除のついでに買い足し"),
        ],
    },
    {
        "slug": "tokushu-winter",
        "short": "冬の備え",
        "title": "冬の備え 消耗品の最安まとめ（カイロ・マスク・ティッシュ）",
        "desc": "貼るカイロ・不織布マスク・ティッシュ・水など、冬に買い置きしたい消耗品を楽天市場の1枚・1本あたり単価で比較。毎朝更新。",
        "lead": "寒さと風邪のシーズンは、カイロ・マスク・ティッシュの減りが早くなります。どれも未開封なら長くもつので、安いときの箱買いが向いています。",
        "months": [11, 12, 1, 2],
        "guide": [
            ("買い置きの目安", "マスクは1人1日1枚として、4人家族なら1か月で約120枚。カイロは通勤・通学で1日1〜2枚使うと、冬のあいだ（約3か月）で1人100〜180枚ほどです。どちらも未開封なら長く保管できるので、安いときの箱買いが向いています。"),
            ("水と電池の備え", "飲み水は1人1日3Lが目安で、最低3日分、できれば1週間分の備蓄がすすめられています。4人家族の3日分なら2Lペットボトルで18本です。停電に備えるライトやラジオは単3電池を使うものが多いので、40本パックを1つ置いておくと安心です。"),
            ("カイロの注意", "貼るカイロは衣類の上から貼り、肌に直接貼らないでください。体温より少し高い温度（44℃前後）でも、同じ場所に数時間当て続けると低温やけどになります。寝るときは使わず、糖尿病などで感覚が鈍くなっている人や、子ども・高齢者は特に注意してください。"),
        ],
        "faq": [
            ("カイロに使用期限はある？", "あります。外袋に使用期限が書かれていて、多くは製造から数年です。期限を過ぎると温かさが弱くなることがあるので、箱買いしたら古いものから使ってください。"),
            ("ミニとレギュラーはどちらが得？", "1枚あたりの値段はミニのほうが安いことが多いですが、温かい時間と面積はレギュラーのほうが上です。腰や背中にはレギュラー、ポケットや首元にはミニ、と使い分けるのが無駄がありません。"),
        ],
        "items": [
            ("kairo", "未開封なら数年もつ。シーズン前の箱買いがいちばん安い"),
            ("mask", "風邪・インフルエンザの季節に。1枚あたりで見ると差が大きい"),
            ("tissue", "鼻かぜの時期は消費が倍に。5箱パックのまとめ買いで"),
            ("water-2l", "雪や停電の備えにも。1人1日3Lが目安"),
            ("aa-battery", "停電時のライト・ラジオ用に"),
            ("tea-500ml", "乾燥する季節の水分補給に。箱買いで1本あたりが下がる"),
        ],
    },
    {
        "slug": "tokushu-supersale",
        "short": "スーパーセール・ブラックフライデー",
        "title": "楽天スーパーセール・ブラックフライデーで買いだめする日用品 最安ガイド",
        "desc": "楽天スーパーセール・楽天ブラックフライデー・お買い物マラソンで買いだめしたい日用品を1回あたり単価で比較。ポイント倍率込みの実質価格にも対応。",
        "lead": "楽天スーパーセール（3・6・9・12月）や楽天ブラックフライデー（2026年は11/19(木)20:00〜11/25(水)1:59）、お買い物マラソンは、ショップの買い回りでポイント倍率が上がります。上の倍率を選ぶと実質価格で表示されます。腐らない・かさばっても使い切る日用品が買いだめ向きです。",
        "months": [3, 6, 9, 11, 12],
        # 開催期間（JST）。期間前は「まもなく開始」、期間中は「開催中」の帯をトップと特集ページに出し、終わったら消える
        "event": {"name": "楽天ブラックフライデー", "s": "2026-11-19T20:00:00+09:00", "e": "2026-11-25T01:59:59+09:00",
                  "pre": "11/19(木)20:00スタート", "on": "11/25(水)1:59まで"},
        "guide": [
            ("ポイントが増えるしくみ", "楽天スーパーセールやお買い物マラソンでは、期間中に買ったショップの数に応じてポイント倍率が上がります（1ショップ1,000円以上の買い物が条件のことが多い）。ふだんのSPU倍率に上乗せされるので、日用品をショップごとに分けて買うと実質価格が大きく下がります。ポイントには上限があるので、高額の買い物は条件を確認してください。"),
            ("買いだめに向くもの", "腐らない・必ず使い切る・かさばっても置ける、の3つがそろうものが買いだめ向きです。トイレットペーパー・洗剤・ペットシーツは向いていて、お米は精米日から1か月くらいで食べ切れる量まで、おむつはサイズアウトするので1〜2か月分までにしておくと失敗がありません。"),
            ("この特集の使い方", "ページ上の「楽天ポイント倍率（SPU）」に自分の倍率を入れると、買い回りの倍率を除いた実質単価に切り替わります。セール中はショップのポイントアップも重なるので、ランキングの順位が入れ替わることがあります。"),
        ],
        "faq": [
            ("楽天スーパーセールはいつ？", "例年3月・6月・9月・12月の上旬〜中旬に開催されています。お買い物マラソンはそれ以外の月にほぼ毎月あります。日程は楽天市場のお知らせで確認してください。"),
            ("楽天ブラックフライデーはいつ？", "2026年は11月19日(木)20:00〜11月25日(水)1:59です（要エントリー）。11/20と11/25は「5と0のつく日」が重なります。例年11月下旬に開催され、スーパーセールと同じく、ショップの買い回りでポイント倍率が上がるので、12月のスーパーセールを待たずに日用品を買いだめする人も多い時期です。日程は楽天市場のお知らせで確認してください。"),
            ("買い回りは何ショップすればいい？", "上限の10ショップまで回ると倍率が最大になります。日用品は1つ1,000円を超えやすいので、洗剤・トイレットペーパー・ペット用品などをショップを分けて買うと、無理なく数をそろえられます。"),
        ],
        "items": [
            ("toilet-paper-double", "かさばるけれど必ず使い切る。長さ（m）あたりで比べる"),
            ("laundry-gelball", "大容量パックは1個あたりで見ると安い"),
            ("diaper-pants-m", "サイズアウトに注意。今のサイズは1〜2か月分まで"),
            ("rice", "精米日から1か月くらいでおいしく食べ切れる量を"),
            ("dog-food-dry", "開封後は1か月が目安。大袋より小分けの多いものが安心"),
            ("cat-litter", "重くてかさばるので、送料込みで比べる"),
            ("protein", "賞味期限が長いので、まとめ買いに向いている"),
        ],
    },
    {
        "slug": "tokushu-furusato",
        "short": "ふるさと納税 日用品",
        "title": "楽天ふるさと納税 日用品のコスパ比較（トイレットペーパー・ティッシュ・お米・水・洗剤）",
        "desc": "楽天ふるさと納税のトイレットペーパー・ティッシュ・お米・水・洗濯洗剤・キッチンペーパーの返礼品を、寄付額あたりの量で比較。寄付1万円でどれだけもらえるかを毎日更新。",
        "lead": "ふるさと納税の日用品は、寄付額あたりの量で比べると返礼品ごとの差が大きく出ます。ここでは楽天ふるさと納税の返礼品を「寄付額÷量」で並べています。今年の控除に入るのは12月31日までの寄付です。",
        "months": [10, 11, 12],
        "guide": [
            ("日用品を選ぶ人が多い理由", "トイレットペーパーやティッシュ、お米は毎日必ず使うので、ふるさと納税でもらえば家計の支出がそのまま減ります。寄付額あたりの量が多く、届いたあとに余らせる心配も少ない返礼品です。"),
            ("このページの見方", "金額はすべて寄付額です。単価は「寄付額÷量」なので、小さいほど同じ寄付でたくさんもらえます。容量を選べる返礼品は、いちばん少ない量と寄付額で計算しています。"),
            ("年末の注意点", "控除の対象になるのは12月31日までに決済が終わった寄付です。年末は申し込みが集中して発送が1〜2か月先になる返礼品もあるので、届く時期と置き場所を確認してから申し込んでください。控除の上限額は年収や家族構成で変わるので、楽天ふるさと納税のシミュレーターなどで確認してください。"),
        ],
        "faq": [
            ("ふるさと納税の自己負担はいくら？", "控除の上限額の範囲内なら、自己負担は年2,000円です。上限を超えた分は控除されないので、先に上限額の目安を確認してください。"),
            ("ワンストップ特例と確定申告の違いは？", "寄付先が1年で5自治体以内で、確定申告をしない会社員などはワンストップ特例の申請書を出せば確定申告がいりません。6自治体以上に寄付した場合や、医療費控除などで確定申告をする場合は、確定申告で寄付金控除を申告します。"),
        ],
        "items": [
            ("furusato-toilet-paper-double", "寄付額の割に量が多い定番。72〜96ロールは段ボールが大きいので置き場所を確認"),
            ("furusato-tissue", "60箱などの大口ほどお得。ソフトパック（箱なし）はかさばりにくい"),
            ("furusato-rice", "10kg・20kgが寄付額あたり多い。精米後は早めに食べきれる量を"),
            ("furusato-water-2l", "重い水を玄関まで届けてもらえる。備蓄用なら保存期間も確認"),
            ("furusato-liquid-laundry-refill", "使い慣れた銘柄の詰め替えまとめが定番"),
            ("furusato-kitchen-paper", "大口ほどお得。かさばるので置き場所を確認"),
        ],
    },
    {
        "slug": "tokushu-baby",
        "short": "赤ちゃん",
        "title": "出産準備・新生児の消耗品 最安まとめ（おむつ・おしりふき・ミルク）",
        "desc": "新生児用おむつ・おしりふき・粉ミルク・液体ミルクを楽天市場の1枚・100gあたり単価で比較。出産準備にどれくらい必要かの目安つき。",
        "lead": "新生児のころは、おむつを1日10〜12枚、おしりふきは1日20〜30枚くらい使います。すぐサイズが変わるので、おむつは買いすぎないのがコツです。",
        "months": [],
        "guide": [
            ("おむつの枚数の目安", "新生児のころは1日10〜12枚、1か月で300枚以上使います。Sサイズのころは1日8〜10枚、Mサイズで7〜8枚くらいに減っていきます。新生児用は体重の増え方によって1か月ほどでサイズアウトする子も多いので、出産前は1〜2パックにして、合うメーカーが分かってから箱買いするのがおすすめです。"),
            ("ミルクの量の目安", "ミルクだけで育てる場合、800gの缶は月齢によって約1〜2週間でなくなります。母乳と混合なら、その半分くらいのペースです。詰め替え用（袋）は缶より100gあたりが安いことが多く、空き缶を使い回せます。"),
            ("調乳と保存の注意", "粉ミルクは、一度沸かして70℃以上に保ったお湯で溶かし、人肌に冷ましてから飲ませます。作ったミルクは2時間以内に飲み切り、残りは捨ててください。液体ミルクは常温で保存でき、開封したらすぐに使い切ります。体重の増え方やミルクの量で気になることがあれば、健診や小児科で相談してください。"),
        ],
        "faq": [
            ("出産前に用意するおむつは？", "新生児用のテープタイプを1〜2パック（60〜140枚ほど）が目安です。メーカーによって肌に合う・合わないがあるので、最初から箱買いしないほうが安心です。"),
            ("粉ミルクと液体ミルクはどちらが安い？", "100mlあたりで比べると粉ミルクのほうがかなり安いです。液体ミルクは調乳がいらず、外出や夜中、災害時の備えに便利なので、ふだんは粉ミルク、いざという時用に液体ミルクを少し置いておく使い分けが多いです。"),
        ],
        "items": [
            ("diaper-tape-nb", "新生児用は1か月ほどでサイズアウトする子も多い。1〜2パックから"),
            ("diaper-tape-s", "体重5kg前後から。新生児用の次に使う"),
            ("baby-wipes", "サイズに関係なく長く使えるので、箱買いしても無駄になりにくい"),
            ("baby-formula", "缶の大きさで100gあたりが変わる。詰め替え用（袋）も安い"),
            ("liquid-milk", "外出や夜中に便利。常温保存できるので備えにも"),
        ],
    },
]


HUBS = [
    {
        "slug": "diaper", "hub": True,
        "short": "紙おむつ サイズ別",
        "title": "紙おむつの最安値 サイズ別比較（新生児〜BIGより大・テープ／パンツ）",
        "desc": "楽天市場の紙おむつを、新生児・S・M（テープ）とM・L・BIG・BIGより大（パンツ）のサイズ別に1枚あたり単価で比較。メリーズ・パンパース・ムーニー・グーン・マミーポコをまとめて毎日更新。",
        "lead": "紙おむつはメーカーより「サイズ」と「入数」で1枚あたりの値段が大きく変わります。今のサイズの最安を確認して、次のサイズはサイズアウトが近づいてからまとめ買いするのが無駄のない買い方です。上の倍率を選ぶとポイント込みの実質価格で表示されます。",
        "months": [],
        "guide": [
            ("サイズの目安（体重）", "メーカーで少しずつ違いますが、テープは新生児用が5kgまで、Sが4〜8kg、Mが6〜11kgくらい。パンツはMが6〜12kg、Lが9〜14kg、BIGが12〜22kg、BIGより大が13〜15kg以上くらいが目安です。体重の範囲が重なるところは、太ももやおなかまわりがきつくなってきたら次のサイズに上げてください。"),
            ("テープからパンツに替える時期", "寝返りやはいはいで動くようになり、寝かせたままテープを留めにくくなったら替えどきです。生後6か月前後、Mサイズのころに切り替える家庭が多いです。夜だけテープ、昼はパンツという使い分けもあります。"),
            ("まとめ買いのコツ", "ケース（3〜4パック）で買うと1枚あたりが安くなりやすい一方、成長が早い時期はサイズアウトで余ることがあります。新生児用とSは1〜2パックずつ、M以降は1か月分くらいを目安にすると失敗が少なくなります。余った未開封のおむつは、フリマアプリや寄付で使ってもらえることもあります。"),
        ],
        "faq": [
            ("紙おむつは1か月に何枚使う？", "新生児のころは1日10〜12枚で月300枚以上、Sサイズで1日8〜10枚、M以降は1日5〜7枚くらいに減っていきます。月齢やうんちの回数で変わるので、目安として考えてください。"),
            ("いちばん安いメーカーはどれ？", "サイズと入数で入れ替わるので一概には言えません。このページは毎日、サイズごとに楽天市場の1枚あたり最安を並べ替えています。各サイズの「ランキングをすべて見る」から、メーカー別の最安も確認できます。"),
        ],
        "items": [
            ("diaper-tape-nb", "新生児用は1か月ほどでサイズアウトする子も多い。1〜2パックから"),
            ("diaper-tape-s", "体重4kgくらいから。テープのいちばん長く使うサイズの1つ"),
            ("diaper-tape-m", "寝返り前の子や、夜だけテープ派に"),
            ("diaper-pants-m", "動きが活発になったら。パンツの中でいちばん売れているサイズ"),
            ("diaper-pants-l", "トイレトレーニング前後まで長く使う。ケース買い向き"),
            ("diaper-pants-big", "BIGは入数が少なめで、1枚あたりの差が開きやすい"),
            ("diaper-pants-xbig", "取り扱いが少ないサイズ。安い出品を見つけたら早めに"),
        ],
    },
    {
        "slug": "toilet-paper", "hub": True,
        "short": "トイレットペーパー",
        "title": "トイレットペーパーの最安値 シングル・ダブル比較（100mあたり）",
        "desc": "楽天市場のトイレットペーパーをシングル・ダブル別に100mあたりの単価で比較。長巻き・まとめ買いの安さ、シングルとダブルの違いも毎日更新のデータで。",
        "lead": "トイレットペーパーはロール数より「長さ（m）」で比べると、長巻きや大容量のどれが本当に安いかが分かります。シングルとダブルは紙の量が違うので、別々に比べています。",
        "months": [],
        "guide": [
            ("シングルとダブル、どちらが得？", "同じ長さならシングルのほうが安く、1ロールも長く巻かれています。ダブルは2枚重ねでやわらかく、1回に使う長さが短くなりがちです。使う長さはシングルがダブルの約1.5倍と言われるので、上の表の100mあたりをそのまま比べず、使い方に合わせて選んでください。"),
            ("長巻き（1.5倍・2倍・3倍）の選び方", "長巻きは交換の手間と収納場所が減り、100mあたりも安くなりやすいです。芯なしや超長巻きはホルダーに入るかどうか（直径）を確認してから選んでください。"),
            ("まとめ買いの目安", "4人家族で月に12ロール（シングル）〜16ロール（ダブル）くらいが目安です。48〜96ロールのケース買いは安いぶん、段ボールが大きいので置き場所を確認してください。"),
        ],
        "faq": [
            ("トイレットペーパー1ロールは何m？", "標準はシングル60m前後、ダブル25〜30m前後です。1.5倍・2倍などの長巻きはその倍数の長さで、このページでは長さを合計して100mあたりで比べています。"),
            ("再生紙とパルプ100%の違いは？", "再生紙（古紙）は安く、パルプ100%は白くてやわらかい傾向です。値段の差は100mあたりで数円〜十数円なので、上の表の各ランキングで確認できます。"),
        ],
        "items": [
            ("toilet-paper-single", "1ロールが長く、100mあたりは安い"),
            ("toilet-paper-double", "2枚重ねでやわらかい。長巻きを選ぶと交換が減る"),
        ],
    },
    {
        "slug": "napkin", "hub": True,
        "short": "生理用ナプキン",
        "title": "生理用ナプキンの最安値 昼用・夜用比較（1枚あたり）",
        "desc": "楽天市場の生理用ナプキンを昼用・夜用別に1枚あたりの単価で比較。ソフィ・ロリエ・エリス・センターインのまとめ買いの最安を毎日更新。",
        "lead": "ナプキンは昼用と夜用で1枚あたりの値段が2倍近く違います。よく使う昼用はまとめ買いで、夜用は必要な枚数だけ、と分けて選ぶと無駄がありません。",
        "months": [],
        "guide": [
            ("昼用と夜用の使い分け", "昼用は20〜25cmくらい、夜用は29〜42cmくらいの長さです。多い日の昼に夜用を使うと安心ですが、1枚あたりは高くなります。量の少ない日は昼用の羽なしなど、安い種類に替えると節約になります。"),
            ("まとめ買いのコツ", "同じ商品でも、1袋よりケース（3〜6袋）のほうが1枚あたりが安くなりやすいです。肌に合う商品が決まってからまとめ買いにすると失敗がありません。"),
        ],
        "faq": [
            ("1回の生理でナプキンは何枚使う？", "昼用は1日4〜6枚、夜用は1日1〜2枚、1回の生理で合計20〜30枚くらいが目安です。量や日数で変わるので、目安として考えてください。"),
            ("肌がかぶれやすいときは？", "表面がコットンの商品や、香料を使っていない商品が向いています。かぶれやかゆみが続くときは皮膚科や婦人科で相談してください。"),
        ],
        "items": [
            ("sanitary-napkin", "毎日使う昼用。まとめ買いで1枚あたりが下がる"),
            ("sanitary-napkin-night", "夜用は1枚あたりが高め。必要な枚数だけ"),
        ],
    },
    {
        "slug": "pet-sheets", "hub": True,
        "short": "ペットシーツ",
        "title": "ペットシーツの最安値 レギュラー・ワイド比較（1枚あたり）",
        "desc": "楽天市場のペットシーツをレギュラー・ワイド別に1枚あたりの単価で比較。薄型・大容量のまとめ買いの最安を毎日更新。",
        "lead": "ペットシーツはサイズで1枚あたりの値段が倍ほど違います。犬の体格に合うサイズの中で、薄型か厚型か、何枚入りかを比べるのが安く買うコツです。",
        "months": [],
        "guide": [
            ("サイズの選び方", "レギュラー（約45×33cm）は小型犬・猫、ワイド（約45×60cm）は小型〜中型犬が目安です。はみ出しやすい子はワイドにすると、床が汚れて交換が増えるより結果的に安くつきます。"),
            ("薄型と厚型", "薄型は安くて収納しやすい一方、1回で替える前提です。厚型は1枚あたり高いですが、数回使えれば1日あたりは下がります。何回で替えるかで比べてください。"),
        ],
        "faq": [
            ("ペットシーツは1日何枚使う？", "小型犬で1日2〜4枚くらいが目安です。月に100枚前後使うなら、400〜800枚のケース買いが1枚あたり最安になりやすいです。"),
            ("レギュラーを2枚並べるのとワイド1枚、どちらが安い？", "1枚あたりの値段がレギュラーの2倍より安いワイドなら、ワイドのほうが得です。上の表で両方の最安を比べてください。"),
        ],
        "items": [
            ("pet-sheet", "小型犬・猫向け。大容量ほど1枚が安い"),
            ("pet-sheet-wide", "はみ出しやすい子に。レギュラー2枚分と比べて選ぶ"),
        ],
    },
    {
        "slug": "contact-lens", "hub": True,
        "short": "コンタクトレンズ",
        "title": "コンタクトレンズの最安値 ワンデー・2week比較（1枚あたり）",
        "desc": "楽天市場のワンデー（1day）と2weekのコンタクトレンズを1枚あたりの単価で比較。アキュビュー・デイリーズ・バイオトゥルーなどの最安を毎日更新。",
        "lead": "ワンデーと2weekは1枚あたりの値段の桁が違いますが、使う日数も違います。1日あたりの費用に直して比べると、自分に合う種類が選びやすくなります。",
        "months": [],
        "guide": [
            ("1日あたりの費用で比べる", "ワンデーは1日に左右2枚、2weekは2枚を14日使います。2weekは1枚あたりが高くても1日あたりは安く、そのぶんケア用品（洗浄液）の費用がかかります。"),
            ("買う前に確認すること", "度数・BC（ベースカーブ）・DIA（直径）は眼科の処方に合わせてください。初めての人や度数が変わった人は、眼科で検査を受けてから購入してください。"),
        ],
        "faq": [
            ("ワンデーと2week、1か月でいくら違う？", "ワンデーは1か月に約60枚、2weekは約4枚使います。上の表の1枚あたりの最安にそれぞれの枚数を掛けると、1か月の費用の目安になります（2weekは洗浄液代が別にかかります）。"),
            ("通販で買っても大丈夫？", "処方された度数・BC・DIAどおりのレンズなら通販でも同じものが届きます。目の痛み・充血があるときは使用をやめて眼科を受診してください。"),
        ],
        "items": [
            ("contact-1day", "毎日新しいレンズ。ケア用品がいらない"),
            ("contact-2week", "1日あたりは安い。洗浄液の費用もふくめて比べる"),
        ],
    },
    {
        "slug": "brush-head", "hub": True,
        "short": "電動歯ブラシ 替えブラシ",
        "title": "電動歯ブラシ 替えブラシの最安値 ソニッケアー・オーラルB比較（1本あたり）",
        "desc": "楽天市場のソニッケアーとオーラルBの替えブラシを1本あたりの単価で比較。純正と互換品の違い、交換時期の目安も。毎日更新。",
        "lead": "替えブラシは純正と互換品で1本あたりの値段が数倍違います。本体のメーカー・型番に合うものの中で、純正か互換品かを決めてから比べると選びやすくなります。",
        "months": [],
        "guide": [
            ("純正と互換品の違い", "互換品は純正の数分の1の値段ですが、毛の品質や耐久性は製品ごとに差があります。レビューの数と評価を見て選ぶと失敗が少なくなります。"),
            ("交換の目安", "どちらのメーカーも約3か月での交換が推奨されています。1年で4本使うので、1本あたりの差が年間の差になります。"),
        ],
        "faq": [
            ("ソニッケアーとオーラルBの替えブラシは共用できる？", "取り付け部分の形が違うので共用できません。お使いの本体のメーカーのランキングから選んでください。"),
            ("互換品を使っても大丈夫？", "取り付けられれば使えますが、メーカーの保証は純正品が前提です。歯ぐきが弱い人は、やわらかめの純正品から試すと安心です。"),
        ],
        "items": [
            ("sonicare-brush-head", "ソニッケアー用。型番（HX6014など）で形を確認"),
            ("oralb-brush-head", "オーラルB用。EB17・EB20などの型番で確認"),
        ],
    },
    {
        "slug": "protein-powder", "hub": True,
        "short": "プロテイン",
        "title": "プロテインの最安値 ホエイ・ソイ比較（100gあたり）",
        "desc": "楽天市場のプロテインをホエイ・ソイ別に100gあたりの単価で比較。大容量・国産の最安を毎日更新。",
        "lead": "プロテインはホエイ（牛乳由来）とソイ（大豆由来）で値段も飲みやすさも違います。100gあたりの値段に加えて、たんぱく質の含有率も見ると本当のコスパが分かります。",
        "months": [],
        "guide": [
            ("ホエイとソイの違い", "ホエイは吸収が早く、運動のあとに向いています。ソイは吸収がゆっくりで腹持ちがよく、乳製品でお腹をこわしやすい人にも向いています。"),
            ("たんぱく質あたりで比べる", "同じ100gでも、たんぱく質の含有率は70〜90%くらいまで差があります。100gあたりの値段を含有率で割ると、たんぱく質1gあたりの値段で比べられます。"),
        ],
        "faq": [
            ("プロテインは1日どれくらい飲む？", "1回20〜30g、1日1〜2回が一般的です。1kgの袋で1か月ほどが目安です。腎臓の病気がある人は医師に相談してください。"),
            ("大容量の袋は得？", "3kg・5kgの大袋は100gあたりが安いですが、味が合わないと飲み切れません。初めての味は1kg以下で試してから大袋にすると失敗がありません。"),
        ],
        "items": [
            ("protein", "ホエイ。運動のあとに。大袋ほど100gあたりが安い"),
            ("protein-soy", "ソイ。腹持ちがよく、乳製品が苦手な人にも"),
        ],
    },
]
HUB_OF = {sl: h for h in HUBS for sl, _ in h["items"]}  # ジャンル → まとめページ


def event_band(f, cls):
    """開催期間の帯。表示はブラウザの現在時刻で切り替える（ビルドは1日1回なので）"""
    ev = f.get("event")
    if not ev:
        return ""
    from datetime import datetime
    if datetime.fromisoformat(ev["e"]) < datetime.now().astimezone():
        return ""
    e = html.escape
    return (f"<span class='{cls}' data-evs='{ev['s']}' data-eve='{ev['e']}' data-pre='{e(ev['name'] + ' ' + ev['pre'])}' "
            f"data-on='{e('開催中：' + ev['name'] + ' ' + ev['on'])}'>{e(ev['name'] + ' ' + ev['pre'])}</span>")


EVENT_JS = ("<script>[].forEach.call(document.querySelectorAll('[data-evs]'),function(x){var n=Date.now();"
            "if(n>Date.parse(x.dataset.eve)){x.remove();return}if(n>=Date.parse(x.dataset.evs)){x.textContent=x.dataset.on;x.className+=' on'}});</script>")


def active(month):
    """今月の特集を先に、それ以外を後ろに"""
    return sorted(FEATURES, key=lambda f: (not event_band(f, ""), month not in f["months"]))


def feature_cards(month):
    e = html.escape
    cards = "".join(
        f"<a class=fc href='{f['slug']}.html'>{'<span class=now>今月</span>' if month in f['months'] else ''}"
        f"<b>{e(f['short'])}</b><span>{e(f['title'])}</span>{event_band(f, 'evb')}</a>" for f in active(month))
    return ("<style>.tokushu{margin-top:22px;scroll-margin-top:120px}.fcs{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}"
            ".fc{position:relative;display:grid;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;color:inherit;text-decoration:none}"
            ".fc:hover{border-color:var(--acc)}.fc b{font-size:1.05rem}.fc span{font-size:.78rem;color:var(--mut);line-height:1.4}"
            ".fc .now{position:absolute;top:8px;right:8px;background:var(--acc);color:#fff;border-radius:6px;padding:0 6px;font-size:.68rem;font-weight:700}"
            ".fc .evb{margin-top:4px;border:1px solid var(--acc);color:var(--acc);border-radius:6px;padding:1px 6px;font-size:.72rem;font-weight:700;line-height:1.5}"
            ".fc .evb.on{background:var(--acc);color:#fff}</style>"
            f"<section class=tokushu id=tokushu><h2>特集</h2><div class=fcs>{cards}</div></section>" + (EVENT_JS if "data-evs" in cards else ""))


def render_feature(f, summary, by_slug, site, updated, short, per_text_of):
    e = html.escape
    url = f"{site}{f['slug']}.html"
    blocks, n_items, toc = "", 0, ""
    for slug, why in f["items"]:
        c, s = by_slug.get(slug), summary.get(slug) or {}
        top = (s.get("top10") if f.get("hub") else None) or s.get("top3") or []
        if not c or not top or s.get("count", 0) < 5:  # 掲載5件未満（検索に載せないページ）は特集に出さない。増えれば自動で戻る
            continue
        n_items += len(top)
        per = per_text_of(c)
        d = 0 if per.startswith("1冊") else 1
        rows = "".join(
            f"<li class=pi><span class=rk>{i}</span><img src='{e(r['i'])}' alt='' loading=lazy width=64 height=64>"
            f"<div><a href='{e(r['u'])}' rel='sponsored noopener' target=_blank>{e(r['n'])}</a>"
            f"<p><b class=up data-u='{r['up']:.4f}' data-pt='{r.get('pt', 1)}' data-d='{d}'>{r['up']:.{d}f}円</b><small>/{e(per)}</small>"
            f" ・ {r['p']:,}円{'（送料込み）' if r.get('fs') else ''}</p></div></li>"
            for i, r in enumerate(top, 1))
        toc += f"<a href='#{slug}'>{e(short(c))}</a>"
        blocks += (f"<section id='{slug}'><h2>{e(short(c))}<small>{e(per)}の安い順</small></h2><p class=why>{e(why)}</p>"
                   f"<ol class=list>{rows}</ol><p class=all><a href='{slug}.html'>{e(short(c))}のランキングをすべて見る（{s.get('count', 0)}件）→</a></p></section>")
    if f.get("hub"):  # まとめページ: 種類・サイズ別の最安と相場を1つの表で比べる（ここにしかない内容）
        trs = ""
        for slug, _ in f["items"]:
            c, s = by_slug.get(slug), summary.get(slug) or {}
            if not c or not s:
                continue
            d = 0 if per_text_of(c).startswith("1冊") else 1
            med = f"{s['med']:,.{d}f}円" if s.get("med") else "—"
            trs += (f"<tr><th><a href='#{slug}'>{e(short(c))}</a></th><td><b>{s['unit_price']:,.{d}f}円</b></td><td>{med}</td>"
                    f"<td>{s.get('count', 0)}件</td></tr>")
        if trs:
            c0 = by_slug.get(f["items"][0][0])
            toc = (f"<table class=cmp><caption>種類別の最安と相場（{e(per_text_of(c0))}・{e(updated[5:10].replace('-', '/'))}時点）</caption>"
                   f"<thead><tr><th>種類</th><th>最安</th><th>相場（中央値）</th><th>掲載</th></tr></thead><tbody>{trs}</tbody></table>") + toc
    guide = "".join(f"<h3>{e(h)}</h3><p>{e(t)}</p>" for h, t in f.get("guide", []))
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in f.get("faq", []))
    extra = (f"<section class=guide><h2>知っておきたいこと</h2>{guide}</section>" if guide else "") + \
            (f"<section class=faq><h2>よくある質問</h2>{faq}</section>" if faq else "")
    others = "".join(f"<a href='{o['slug']}.html'>{e(o['title'])}</a>" for o in (HUBS if f.get("hub") else FEATURES) if o is not f)
    lds = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "TANKA", "item": site},
        {"@type": "ListItem", "position": 2, "name": f["title"], "item": url}]}]
    if f.get("faq"):
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in f["faq"]]})
    ld = json.dumps(lds, ensure_ascii=False)
    robots = "" if n_items >= 6 else "<meta name=robots content=noindex>"
    return (PAGE.replace("@@TITLE@@", e(f["title"] + "｜TANKA")).replace("@@DESC@@", e(f["desc"])).replace("@@URL@@", e(url))
            .replace("@@ROBOTS@@", robots).replace("@@LD@@", ld).replace("@@H1@@", e(f["title"])).replace("@@LEAD@@", e(f["lead"]))
            .replace("@@EVENT@@", (f"<p>{event_band(f, 'evp')}</p>" + EVENT_JS) if event_band(f, 'evp') else "")
            .replace("@@TOC@@", toc).replace("@@BLOCKS@@", blocks or "<p>集計中です。</p>").replace("@@OTHERS@@", others).replace("@@EXTRA@@", extra)
            .replace("@@UPDATED@@", e(updated[5:10].replace("-", "/") + " " + updated[11:]))
            .replace("@@CRUMB@@", "種類別まとめ" if f.get("hub") else "特集").replace("@@OTHERHEAD@@", "ほかのまとめ" if f.get("hub") else "ほかの特集"))


PAGE = """<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>@@TITLE@@</title>
<meta name=description content="@@DESC@@">@@ROBOTS@@
<link rel=canonical href="@@URL@@">
<meta property="og:title" content="@@TITLE@@"><meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@URL@@"><meta property="og:type" content="article"><meta name="twitter:card" content="summary">
<script type="application/ld+json">@@LD@@</script>
<style>:root{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--card:#f5f5f7;--line:#e3e3e8;--acc:#bf0000;--ok:#0a7d4f}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6;--card:#1c1c1e;--line:#333;--acc:#ff6b6b;--ok:#4cd38f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 system-ui,sans-serif}
main{max-width:760px;margin:auto;padding:16px}a{color:inherit}h1{font-size:1.35rem;line-height:1.4;margin:.2em 0 .4em}
.mut{color:var(--mut);font-size:.85rem}.pr{font-size:.75rem;color:var(--mut)}
.spu{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font-size:.85rem;margin:12px 0}
.spu select{font:inherit;padding:3px 6px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}.toc a{border:1px solid var(--line);border-radius:999px;padding:3px 10px;text-decoration:none;font-size:.85rem;background:var(--card)}
section{scroll-margin-top:12px}h2{font-size:1.1rem;margin:1.8em 0 .2em}h2 small{font-weight:400;color:var(--mut);font-size:.78rem;margin-left:8px}
.why{margin:0 0 6px;color:var(--mut);font-size:.88rem}
.list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.pi{display:flex;gap:10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 10px}
.pi img{width:64px;height:64px;object-fit:contain;background:#fff;border-radius:8px;flex:none}.pi div{min-width:0}
.pi a{font-size:.88rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pi p{margin:2px 0 0;font-size:.8rem;color:var(--mut)}.pi b{color:var(--acc);font-size:1.1rem}
.rk{flex:none;width:1.6em;height:1.6em;line-height:1.6em;text-align:center;border-radius:50%;background:var(--acc);color:#fff;font-size:.75rem;font-weight:700}
.all{margin:6px 0 0;font-size:.88rem}.all a{color:var(--ok);font-weight:600}
.others{display:grid;gap:6px;margin-top:8px}.others a{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;text-decoration:none;font-size:.9rem}
.guide h3{font-size:.95rem;margin:1.2em 0 .2em}.guide p{margin:0;font-size:.92rem}
.faq details{border-bottom:1px solid var(--line);padding:8px 0}.faq summary{cursor:pointer;font-weight:600}.faq p{margin:.4em 0 0;font-size:.92rem}
.evp{display:inline-block;border:1px solid var(--acc);color:var(--acc);border-radius:8px;padding:2px 10px;font-weight:700;font-size:.92rem}.evp.on{background:var(--acc);color:#fff}
.cmp{width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem}.cmp caption{text-align:left;color:var(--mut);font-size:.8rem;margin-bottom:4px}
.cmp th,.cmp td{border-bottom:1px solid var(--line);padding:6px 4px;text-align:right}.cmp th:first-child{text-align:left}.cmp td b{color:var(--acc)}
footer{margin-top:28px;color:var(--mut);font-size:.8rem}</style></head><body><main>
<p class=mut><a href="./">TANKA</a> › @@CRUMB@@</p>
<p class=pr>PR：楽天アフィリエイトを利用しています</p>
<h1>@@H1@@</h1>
@@EVENT@@<p>@@LEAD@@</p>
<div class=spu><label for=spu>楽天ポイント倍率（SPU）</label><select id=spu><option value=0>未設定</option></select><span id=spumsg class=mut></span></div>
<nav class=toc aria-label="目次">@@TOC@@</nav>
@@BLOCKS@@
@@EXTRA@@
<h2>@@OTHERHEAD@@</h2><div class=others>@@OTHERS@@</div>
<footer><p>価格は @@UPDATED@@ 時点で楽天市場から取得したものです。毎日自動で更新しています。購入前に商品ページで確認してください。</p>
<p><a href="./">トップへ戻る</a> ・ <a href="calc.html">単価計算ツール</a> ・ <a href="about.html">このサイトについて</a></p></footer>
</main>
<script>
(function(){
  var sel=document.getElementById('spu'), msg=document.getElementById('spumsg'), ups=[].slice.call(document.querySelectorAll('.up'));
  for(var k=1;k<=20;k++){var o=document.createElement('option');o.value=k;o.textContent=k+'倍';sel.appendChild(o);}
  function spu(v){
    ups.forEach(function(b){var u=+b.dataset.u, d=+b.dataset.d;
      if(v>0){b.textContent='実質'+(u*(1-(v+(+b.dataset.pt||1)-1)/110)).toFixed(d)+'円';} else b.textContent=u.toFixed(d)+'円';});
    msg.textContent=v>0?'ショップのポイントアップも足した実質価格です':'';
  }
  var saved=0; try{saved=+localStorage.getItem('tanka_spu')||0}catch(e){}
  if(saved){sel.value=saved; spu(saved);}
  sel.addEventListener('change',function(){var v=+sel.value; try{localStorage.setItem('tanka_spu',v)}catch(e){} spu(v);
    if(window.gtag) gtag('event','set_spu',{value:v});});
})();
</script></body></html>"""
