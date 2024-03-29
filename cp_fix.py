import copy
import datetime
import json
import os
import re
import shutil
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# タイムスタンプ用変数
d: str = str(datetime.datetime.now()).split('.')[0]
d: str = d.replace('-', '')
d: str = d.replace(' ', '')
_stamp: str = d.replace(':', '')


def read_json(path: str) -> list[str, dict]:  # config ファイルを変数と JSON（dict）に変換して戻す
    reg: str = '(^var.+=)([\s\S]+)|;'
    f = open(path, 'r', encoding="utf-8")
    s: str = f.read()
    f.close()

    dec: str = re.sub(reg, '\\1', s)  # 変数名
    j: str = re.sub(reg, '\\2', s).replace(';', '')  # セミコロンを除去

    json_data: dict = json.loads(j)  # JSON 部分

    return [dec, json_data]


def time_stampID() -> int:
    return int(time.time()*1000)


# スライド設定のチェック
def fix_slides_settings(d: dict, id: str) -> None:

    commonInfo: dict = d['commonInfo']
    cmnWidth: int = commonInfo['idvWidth']
    cmnHeight: int = commonInfo['idvHeight']
    slides_height: int = 176
    slides_heightP: str = f'{slides_height / cmnHeight * 100}%'
    slides_width: int = 249
    slides_widthP: str = f'{slides_width / cmnWidth * 100}%'
    slides_top: int = 1245
    slides_topP: str = f'{slides_top / cmnHeight * 100}%'
    slides_left_R: int = 1776
    slides_left_L: int = 123
    slides_len: int = len(d['chapterInfo']['pageInfos'])

    # チャプター名設定
    d['chapterInfo']['name'] = 'スライド'

    for p in d['chapterInfo']['pageInfos']:
        clickPoint: dict = p['clickPoint']

        cwn: int = int(p['pageIndex'])  # 現在のページ

        # スライド画像の設定
        if p['filename'][0] != 'k':
            p['filename'] = f'{id}_{chapter_num}-{cwn}.webp'

        # 教科書学年 ID の取得 2Aなど
        kind_id: str = re.sub('KSK_R6_SANSU_(\d.)_[TDM]', '\\1', j['commonInfo']['cmnBookId'])

        # スライドサムネイル画像リンク生成（前・次）
        prev_thum: str = f'thum_{kind_id}_{chapter_num}-{cwn - 1}.png'
        next_tum: str = f'thum_{kind_id}_{chapter_num}-{cwn + 1}.png'

        thum_arr = []
        # クリックポイントを個別にチェック
        for cp in clickPoint:

            # icon リンク画像名に「'thum_'」が含まれる場合
            if cp['cpIcon'] != '' and 'thum_' in cp['cpIcon']:
                thum_arr.append(cp)

                # ID の再設定
                _id: int = time_stampID()
                cp['cpId'] = _id
                cp['cpUId'] = f'cd_{_id}'
                cp['resInfo']["resId"] = f'rsc_cp_{_id}'

                time.sleep(.001)
                # 遷移先を[別タブ]に変更
                cp['resInfo']['resType'] = 4
                cp['resInfo']['resLink']['type'] = 5

                # 遷移先チャプタ
                cp['resInfo']['resLink']['chapter'] = chapter_num

                # 1スライド目
                if cwn == 1:
                    # リンク画像の設定
                    cp['cpIcon'] = next_tum

                    # 右スライド位置設定
                    cp['cpLeft'], cp['cpLeftP'] = slides_left_R, f'{slides_left_R / cmnWidth * 100}%'

                    # 遷移先（次のページ）
                    cp['resInfo']['resLink']['pageIdx'] = cwn + 1

                # 最後のスライド
                elif cwn == slides_len:
                    # サムネイル画像の設定（前のページ）
                    cp['cpIcon'] = prev_thum

                    # 左スライド位置設定
                    cp['cpLeft'], cp['cpLeftP'] = slides_left_L, f'{slides_left_L / cmnWidth * 100}%'

                    # 遷移先（次のページ）
                    cp['resInfo']['resLink']['pageIdx'] = cwn - 1

                # 高さ設定
                cp['cpHeight'], cp['cpHeightP'] = slides_height, slides_heightP

                # 幅設定
                cp['cpWidth'], cp['cpWidthP'] = slides_width, slides_widthP

                # top 位置調整
                cp['cpTop'], cp['cpTopP'] = slides_top, slides_topP

                # 透過設定
                cp['cpAlpha'] = '1.0'

        # 最初と終わり以外のスライド、サムネイル設定
        if cwn != 1 and cwn != slides_len:
            # 配列の最初が左側のクリックポイントの場合は、配列を逆順に変更
            if thum_arr[0]['cpLeft'] > thum_arr[1]['cpLeft']:
                thum_arr.reverse()

            # サムネイル位置（左）
            thum_arr[0]['cpLeft'], thum_arr[0]['cpLeftP'] = slides_left_L, f'{slides_left_L / cmnWidth * 100}%'

            # サムネイル位置（右）
            thum_arr[1]['cpLeft'], thum_arr[1]['cpLeftP'] = slides_left_R, f'{slides_left_R / cmnWidth * 100}%'

            # リンク画像の確認（左）
            thum_arr[0]['cpIcon'] = prev_thum
            # リンク画像の確認（右）
            thum_arr[1]['cpIcon'] = next_tum

            # 遷移先（左）
            thum_arr[0]['resInfo']['resLink']['pageIdx'] = cwn - 1
            # 遷移先（右）
            thum_arr[1]['resInfo']['resLink']['pageIdx'] = cwn + 1


'''-------------------------------------------
----------------------------------------------
----------------------------------------------
----------------------------------------------
-------------------------------------------'''


def cp_style_fix(d: dict, id: str) -> None:  # クリックポイントのスタイル修正
    # クリックポイントを個別にチェック
    for p in d['chapterInfo']['pageInfos']:
        clickPoint: dict = p['clickPoint']

        mekuris = []
        # クリックポイントを個別にチェック
        for cp in clickPoint:

            # 画像が設定されている cp
            cp['cpAlpha'] = -1 if cp['cpIcon'] != "" else None  # 不透過に変更

            # めくり紙-別指定
            if cp['resInfo']['resMekuri']['type'] == 2:
                cp['cpAlpha'] = '0' if cp['cpAlpha'] != '0' else None  # 透明に変更
                mekuris = mekuris + cp['resInfo']['resMekuri']['target']

        print(mekuris)
'''-------------------------------------------
----------------------------------------------
----------------------------------------------
----------------------------------------------
-------------------------------------------'''


if __name__ == '__main__':

    cwd = Path(os.path.dirname(__file__))
    configs_dir = cwd.joinpath('configs')
    configs: list = list(configs_dir.glob('ffl-chapter_*-config.js'))
    bk_dir = cwd.joinpath(Path('configs'), Path('_backup'))

    for cnf in configs:
        bn: str = os.path.splitext(os.path.basename(cnf))[0]  # オリジナルファイル - 拡張子なし
        d: str = read_json(cnf)[0]  # 変数部分
        j: dict = read_json(cnf)[1]  # JSON 部分
        df: dict = copy.deepcopy(j)  # 比較用に Original を変数にコピー代入

        # cmnBookId に KSK_ ... がない場合は処理しない
        # if 'KSK_' not in j['commonInfo']['cmnBookId']:
        #     print('対象外ファイル:', bn)
        #     continue

        k_id: str = re.sub('KSK_R6_SANSU_(\d.)_[TDM]', '\\1', j['commonInfo']['cmnBookId'])

        # スライド設定調整
        chapter_num: int = j['chapterInfo']['chapter']
        if chapter_num >= 101 or chapter_num <= 399:
            fix_slides_settings(j, k_id)
            cp_style_fix(j, k_id)
            pass

        # 変更がなければ処理終了
        if df == j:
            print('変更なし:', bn)
            continue

        print('変更あり:', bn)
        # backup ディレクトリ作成
        if os.path.isdir(bk_dir) != True:
            os.mkdir(bk_dir)

        # 元ファイルを bacuup フォルダにコピー / backup ファイル名のリネーム
        shutil.copyfile(cnf, Path(f'{bk_dir}/{bn}_{_stamp}'))
        f = open(Path(f'{cwd}/configs/{os.path.basename(cnf)}'), 'w', encoding="utf-8")

        # 変数部分と結合
        n_d = (d + ' ' + json.dumps(j, ensure_ascii=False)).replace('\n', '') + ';'
        f.write(n_d)
        f.close()

    messagebox.showinfo('処理終了', '処理が正常に完了しました')
    root = tk.Tk()
    root.withdraw()
