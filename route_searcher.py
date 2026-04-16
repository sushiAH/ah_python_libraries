import random
"""
ID	カテゴリ	アクション名	補足
1	移動	段差上り	+1 の段差へ進む
2	移動	段差降り	-1 の段差へ進む
3	移動	そのまま移動	同じ高さのまま前進
4	正面取得	正面取得（右腕 / 同じ）	1個目 / 正面 / 高さ±0
5	正面取得	正面取得（右腕 / 下）	1個目 / 正面 / 高さ-1
6	正面取得	正面取得（右腕 / 上）	1個目 / 正面 / 高さ+1
7	正面取得	正面取得（左腕 / 同じ）	2個目 / 正面 / 高さ±0
8	正面取得	正面取得（左腕 / 下）	2個目 / 正面 / 高さ-1
9	正面取得	正面取得（左腕 / 上）	2個目 / 正面 / 高さ+1
10	左側取得	左側取得（右腕 / 同じ）	1個目 / 左側 / 高さ±0
11	左側取得	左側取得（右腕 / 下）	1個目 / 左側 / 高さ-1
12	左側取得	左側取得（右腕 / 上）	1個目 / 左側 / 高さ+1
13	左側取得	左側取得（左腕 / 同じ）	2個目 / 左側 / 高さ±0
14	左側取得	左側取得（左腕 / 下）	2個目 / 左側 / 高さ-1
15	左側取得	左側取得（左腕 / 上）	2個目 / 左側 / 高さ+1
16	右側取得	右側取得（右腕 / 同じ）	1個目 / 右側 / 高さ±0
17	右側取得	右側取得（右腕 / 下）	1個目 / 右側 / 高さ-1
18	右側取得	右側取得（右腕 / 上）	1個目 / 右側 / 高さ+1
19	右側取得	右側取得（左腕 / 同じ）	2個目 / 右側 / 高さ±0
20	右側取得	右側取得（左腕 / 下）	2個目 / 右側 / 高さ-1
21	右側取得	右側取得（左腕 / 上）	2個目 / 右側 / 高さ+1
22	廃棄	廃棄（左腕）	1回目の廃棄
23	廃棄	廃棄（右腕）	2回目の廃棄
24	準備	位置確認・真ん中移動	移動完了直後の姿勢制御
25	進入	0列目進入（取得あり）	進入時に正面の箱を取得
26	進入	1列目進入（取得あり）	進入時に正面の箱を取得
27	進入	2列目進入（取得あり）	進入時に正面の箱を取得
28	進入	0列目進入（取得なし）	取得せずに進入
29	進入	1列目進入（取得なし）	取得せずに進入
30	進入	2列目進入（取得なし）	取得せずに進入
31	最終移動	0列目から地点移動	退出後、指定地点へ移動
32	最終移動	1列目から地点移動	退出後、指定地点へ移動
33	最終移動	2列目から地点移動	退出後、指定地点へ移動
"""

# 高さマップ
HEIGHT_MAP = [[1, 0, 1], [0, 1, 2], [1, 2, 1], [0, 1, 0]]


def get_id_name(aid):
    fixed = {
        1: "段差上り",
        2: "段差降り",
        3: "そのまま移動",
        22: "廃棄(左)",
        23: "廃棄(右)",
        24: "位置確認・真ん中移動",
        25: "0列目進入(取有)",
        26: "1列目進入(取有)",
        27: "2列目進入(取有)",
        28: "0列目進入(取無)",
        29: "1列目進入(取無)",
        30: "2列目進入(取無)",
        31: "0列目地点移動",
        32: "1列目地点移動",
        33: "2列目地点移動"
    }
    if aid in fixed:
        return fixed[aid]
    base = (aid - 4) // 6  # 0:正面, 1:左, 2:右
    arm = "右腕" if ((aid - 4) % 6) < 3 else "左腕"
    h = ["同じ", "下", "上"][(aid - 4) % 3]
    return f"{['正面','左側','右側'][base]}取得({arm}/{h})"


def create_random_items():
    cells = [1] * 4 + [2] * 1 + [0] * 7
    random.shuffle(cells)
    return [cells[i:i + 3] for i in range(0, 12, 3)]


def solve_full_operation(item_grid, height_grid):
    rows, cols, ground_h = 4, 3, 0
    valid_results = []

    for c in range(cols):
        # 基本チェック
        if any(item_grid[r][c] == 2 for r in range(rows)):
            continue
        h_seq = [ground_h] + [height_grid[r][c] for r in range(rows)
                             ] + [ground_h]
        if any(abs(h_seq[i] - h_seq[i + 1]) > 1 for i in range(len(h_seq) - 1)):
            continue

        mandatory_items = [(r, c) for r in range(rows) if item_grid[r][c] == 1]
        inventory, path_flow, handled_items = [], [], set()
        current_h, pickup_total, discard_total = ground_h, 0, 0
        full_seq = []

        for r in range(rows):
            target_pos, h_target, step_ids = (r, c), height_grid[r][c], []

            if r == 0:
                # --- 進入例外 ---
                if item_grid[r][c] == 1:
                    step_ids.append(25 + c)
                    inventory.append(target_pos)
                    handled_items.add(target_pos)
                    pickup_total += 1  # 1個目: 左腕使用とみなす
                else:
                    step_ids.append(28 + c)
                step_ids.append(24)  # 進入直後の姿勢制御
                current_h = h_target
            else:
                # --- 通常移動 ---
                if item_grid[r][c] == 1 and target_pos not in inventory:
                    if len(inventory) >= 2:
                        discard_total += 1
                        # 1個目(左)を捨てるなら22, 2個目(右)を捨てるなら23
                        step_ids.append(22 if discard_total == 1 else 23)
                        inventory.pop(0)

                    pickup_total += 1
                    h_idx = 0 if h_target == current_h else (
                        1 if h_target < current_h else 2)

                    # 【変更点】 1個目(inventory空)ならオフセット3(左腕)、2個目なら0(右腕)
                    arm_offset = 3 if len(inventory) == 0 else 0
                    step_ids.append(4 + arm_offset + h_idx)

                    inventory.append(target_pos)
                    handled_items.add(target_pos)

                diff = h_target - current_h
                step_ids.append(1 if diff > 0 else (2 if diff < 0 else 3))
                current_h = h_target
                step_ids.append(24)  # 移動後の姿勢制御

            # 周囲スキャン
            for pr, pc, side, b_idx in [(r, c + 1, "L", 1), (r, c - 1, "R", 2),
                                        (r + 1, c, "F", 0)]:
                if 0 <= pr < rows and 0 <= pc < cols:
                    if item_grid[pr][pc] == 1 and (pr,
                                                   pc) not in inventory and (
                                                       pr,
                                                       pc) not in handled_items:
                        if abs(height_grid[pr][pc] - current_h) <= 1:
                            future_man = len([
                                p for p in mandatory_items if p[0] > r or
                                (p == target_pos and p not in inventory)
                            ])
                            if len(inventory) + future_man < 2:
                                pickup_total += 1
                                h_idx = 0 if height_grid[pr][
                                    pc] == current_h else (
                                        1 if height_grid[pr][pc] < current_h
                                        else 2)

                                # 【変更点】 1個目ならオフセット3(左腕)、2個目なら0(右腕)
                                arm_offset = 3 if len(inventory) == 0 else 0
                                step_ids.append(4 + (b_idx * 6) + arm_offset +
                                                h_idx)

                                inventory.append((pr, pc))
                        handled_items.add((pr, pc))

            path_flow.append({
                "row": r,
                "ids": step_ids,
                "inv": list(inventory)
            })
            full_seq.extend(step_ids)

        # --- 脱出 ---
        diff_exit = ground_h - current_h
        exit_move_id = 1 if diff_exit > 0 else (2 if diff_exit < 0 else 3)
        full_seq.append(exit_move_id)

        # --- 最終地点への移動 (31-33) ---
        full_seq.append(31 + c)

        path_flow.append({
            "row": "EXIT",
            "ids": [exit_move_id, 31 + c],
            "inv": list(inventory)
        })

        if len(inventory) == 2:
            valid_results.append({
                "column": c,
                "flow": path_flow,
                "seq": full_seq,
                "count": len(full_seq)
            })

    return valid_results


def calc_on_step_sequence(items):
    print("\n[ フィールド状況 ]")
    for r in range(4):
        print(f" r{r} | " + " ".join([
            f"[{'📦' if items[r][c]==1 else ('🧱' if items[r][c]==2 else '␣')}:{HEIGHT_MAP[r][c]}]"
            for c in range(3)
        ]))

    routes = solve_full_operation(items, HEIGHT_MAP)
    print("\n" + "=" * 75 + "\n      完全運用シミュレーション（左腕優先取得版）\n" + "=" * 75)

    if not routes:
        print("\nクリア可能なルートなし")
        return None
    else:
        for r in routes:
            print(f"\n○ オプション：列 {r['column']} (総計 {r['count']} 手)")
            for s in r['flow']:
                print(
                    f"  Row {s['row']}: [{','.join(map(str, s['ids']))}] ({' + '.join([get_id_name(i) for i in s['ids']])})"
                )

        best = min(routes, key=lambda x: x['count'])
        print(
            "\n" + "🏆" * 37 +
            f"\n      最終採用エリート・ルート：列 {best['column']} (最短 {best['count']} 手)\n"
            + "🏆" * 37)
        print(f"  確定フルコマンド配列：{best['seq']}")
        return best


if __name__ == "__main__":
    items = create_random_items()
    calc_on_step_sequence(items)
