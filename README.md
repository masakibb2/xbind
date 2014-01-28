xbind
=====

ligand binding residue predictor generator in UTProt Galaxy


UTProt Galaxy リンガンド結合部位予測ツール生成パイプライン

概要
生命システムの解明には、タンパク質のリガンド結合部位の解析が重要であるが、生化学実験や構造決定などの実験的手法は、一般に複雑な手順・高額な装置・研究者の熟練等が必要である。そこで、バイオインフォマティクスの手法を用いたリガンド結合部位予測・解析システムが期待されている。

UTProt Galaxy は、統一的なフレームワークで、利用者の目的にあった精度の高いリガンド結合部位予測ツールを、最新のデータを統合することにより、自動的に生成するシステムを構築した。生成される予測ツールは立体構造未知なタンパク質も予測可能で計算コストも小さく、ゲノムワイドな予測が可能である。

UTProt Galaxy は、データセット生成パイプライン、予測ツール生成パイプライン、リガンド結合部位予測パイプラインの3つのパイプラインで構成されている。

データセット生成パイプラインは、タンパク質アミノ酸配列データベース UniProt、タンパク質立体構造データベース Protein Data Bank (PDB)、及び UniProt の間の相互参照情報を記述した EBI-SIFTSと、我々が開発したリガンド結合部位データベースである Protein Lgaind Binding Pair Database (PLBSP) を統合検索することで、ユーザーが指定したリガンドと結合するタンパク質のアミノ酸配列およびリガンド結合部位を取得する。

予測ツール生成パイプラインでは、データセット生成パイプラインが取得してきたデータをもとに機械学習の手法を用いて、リガンド結合部位予測ツールを自動的に生成する。

リガンド結合部位予測パイプラインは、予測ツール生成パイプラインで生成した予測ツールに結合部位を予測したいアミノ酸配列を入力し、どのアミノ酸残基が結合部位となり得るか予測する。

UTProt Galaxy は、これまで多くの時間や労力を必要としてきたリガンド結合部位の予測をWebベースで比較的短時間で実行することが可能となり、生命科学の研究効率化・コスト削減につながることが期待される。

参考

JST NBDC 統合化推進プログラム（統合データ解析トライアル）平成25年度
中間報告資料（操作チュートリアルを含む）
UTProt Galaxy Quick Start （上記資料のチュートリアル部のみ）
UTProt Galaxy Module Documantation （パイプライン中のモジュールの仕様書）
UTProt （プロジェクトポータルサイト、http://utprot.net）
アプリケーションで利用したデータセット
PLBSP (http://utprot.net/index.php/semantic_web/plbsp-lod/)
wwPDB/RDF (http://rdf.wwpdb.org/pdb/)
UniProt (http://www.uniprot.org/)
EBI-SIFTS (http://www.ebi.ac.uk/pdbe/docs/sifts/)
 Download
https://github.com/masakibb2/xbind

連絡先
開発者　番野 雅城
masaki070540@bi.a.u-tokyo.ac.jp

東京大学大学院　農学生命科学研究科
応用生命工学専攻　生物情報工学研究室
