import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# 체크박스 상태를 나타내는 특수문자
CHECKED = "☑"
UNCHECKED = "☐"

# 파일 경로 저장을 위한 딕셔너리
file_data_map = {}

def select_source_folder():
    path = filedialog.askdirectory()
    if path:
        entry_source.delete(0, tk.END)
        entry_source.insert(0, path)

def select_target_folder():
    path = filedialog.askdirectory()
    if path:
        entry_target.delete(0, tk.END)
        entry_target.insert(0, path)

def search_files():
    """조건에 맞는 파일을 찾아 리스트에 '체크된 상태'로 표시"""
    source_dir = entry_source.get()
    extensions = entry_ext.get().replace(" ", "").split(",")
    keywords = entry_keyword.get().split(",")
    
    if not source_dir:
        messagebox.showwarning("경고", "원본 폴더를 선택해주세요.")
        return

    # 리스트 초기화
    tree_list.delete(*tree_list.get_children())
    file_data_map.clear()
    
    count = 0
    lbl_status.config(text="파일 스캔 중...")
    root.update()

    try:
        for root_path, dirs, files in os.walk(source_dir):
            for file in files:
                # 1. 확장자 체크
                file_ext = file.split('.')[-1].lower()
                if file_ext in [ext.lower() for ext in extensions]:
                    
                    # 2. 키워드 체크
                    should_include = False
                    if not entry_keyword.get().strip(): 
                        should_include = True
                    else:
                        for key in keywords:
                            if key.strip().lower() in file.lower():
                                should_include = True
                                break
                    
                    if should_include:
                        full_path = os.path.join(root_path, file)
                        size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
                        
                        # Treeview에 추가 (기본값: CHECKED)
                        # values = (체크박스, 파일명, 크기, 경로)
                        item_id = tree_list.insert('', 'end', values=(CHECKED, file, f"{size_mb} MB", root_path))
                        
                        file_data_map[item_id] = full_path
                        count += 1
        
        lbl_status.config(text=f"검색 완료: 총 {count}개의 파일을 찾았습니다.")
        
    except Exception as e:
        messagebox.showerror("에러", str(e))

def toggle_check(event):
    """리스트를 클릭했을 때 체크박스 상태 토글"""
    item_id = tree_list.identify_row(event.y)
    if not item_id:
        return

    # 현재 값 가져오기
    current_values = tree_list.item(item_id, "values")
    current_status = current_values[0]
    
    # 상태 반전
    new_status = UNCHECKED if current_status == CHECKED else CHECKED
    
    # 값 업데이트 (튜플은 수정 불가능하므로 리스트로 변환 후 다시 튜플로)
    new_values = list(current_values)
    new_values[0] = new_status
    tree_list.item(item_id, values=new_values)

def set_all_selection(state):
    """전체 선택 또는 전체 해제"""
    symbol = CHECKED if state else UNCHECKED
    for item_id in tree_list.get_children():
        current_values = tree_list.item(item_id, "values")
        new_values = list(current_values)
        new_values[0] = symbol
        tree_list.item(item_id, values=new_values)

def copy_checked_files():
    """체크 표시(☑)가 된 파일만 복사 실행"""
    target_dir = entry_target.get()
    
    if not target_dir:
        messagebox.showwarning("경고", "저장할 폴더를 선택해주세요.")
        return

    # 체크된 아이템 찾기
    checked_items = []
    for item_id in tree_list.get_children():
        values = tree_list.item(item_id, "values")
        if values[0] == CHECKED:
            checked_items.append(item_id)
    
    if not checked_items:
        messagebox.showwarning("알림", "복사할 파일이 선택되지 않았습니다.\n체크박스를 확인해주세요.")
        return

    # 확인 창
    ans = messagebox.askyesno("복사 시작", f"총 {len(checked_items)}개의 파일을 복사하시겠습니까?")
    if not ans:
        return

    count = 0
    lbl_status.config(text="복사 시작...")
    
    try:
        for item_id in checked_items:
            src_path = file_data_map[item_id]
            file_name = os.path.basename(src_path)
            dst_path = os.path.join(target_dir, file_name)
            
            shutil.copy2(src_path, dst_path)
            count += 1
            lbl_status.config(text=f"복사 중 ({count}/{len(checked_items)}): {file_name}")
            root.update()
            
        messagebox.showinfo("성공", f"작업 완료!\n{count}개의 파일을 성공적으로 복사했습니다.")
        lbl_status.config(text="대기 중")
        
    except Exception as e:
        messagebox.showerror("복사 에러", str(e))
        lbl_status.config(text="오류 발생")

# --- GUI 설정 ---
root = tk.Tk()
root.title("스마트 음원 정리기 v3")
root.geometry("800x600")

style = ttk.Style()
style.configure("Treeview", rowheight=25) # 행 높이 조절

padding_opts = {'padx': 10, 'pady': 5}

# 1. 상단 입력부
frame_top = tk.Frame(root)
frame_top.pack(fill='x', **padding_opts)

tk.Label(frame_top, text="원본 폴더:").grid(row=0, column=0, sticky='w')
entry_source = tk.Entry(frame_top, width=60)
entry_source.grid(row=0, column=1, padx=5)
tk.Button(frame_top, text="선택", command=select_source_folder).grid(row=0, column=2)

tk.Label(frame_top, text="저장 폴더:").grid(row=1, column=0, sticky='w')
entry_target = tk.Entry(frame_top, width=60)
entry_target.grid(row=1, column=1, padx=5)
tk.Button(frame_top, text="선택", command=select_target_folder).grid(row=1, column=2)

tk.Label(frame_top, text="확장자:").grid(row=2, column=0, sticky='w')
entry_ext = tk.Entry(frame_top, width=60)
entry_ext.insert(0, "wav, mp3") # 기본값
entry_ext.grid(row=2, column=1, padx=5)

tk.Label(frame_top, text="키워드:").grid(row=3, column=0, sticky='w')
entry_keyword = tk.Entry(frame_top, width=60)
entry_keyword.grid(row=3, column=1, padx=5)

# 2. 검색 버튼
tk.Button(root, text="🔍 파일 스캔 시작", command=search_files, bg="#eeeeee", height=2).pack(fill='x', padx=10, pady=5)

# 3. 리스트 (Treeview)
frame_list = tk.Frame(root)
frame_list.pack(fill='both', expand=True, padx=10)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side='right', fill='y')

# 컬럼 정의: check(선택), filename(이름), size(크기), path(경로)
columns = ("check", "filename", "size", "path")
tree_list = ttk.Treeview(frame_list, columns=columns, show='headings', yscrollcommand=scrollbar.set)

# 헤더 설정
tree_list.heading("check", text="선택")
tree_list.heading("filename", text="파일 이름")
tree_list.heading("size", text="크기")
tree_list.heading("path", text="경로")

# 컬럼 너비 설정
tree_list.column("check", width=50, anchor='center')
tree_list.column("filename", width=250)
tree_list.column("size", width=80, anchor='center')
tree_list.column("path", width=350)

tree_list.pack(fill='both', expand=True)
scrollbar.config(command=tree_list.yview)

# 클릭 이벤트 연결 (클릭 시 체크박스 토글)
tree_list.bind('<Button-1>', toggle_check)

# 4. 하단 액션 버튼
frame_action = tk.Frame(root)
frame_action.pack(fill='x', **padding_opts)

# 전체 선택/해제 버튼
tk.Button(frame_action, text="☑ 전체 선택", command=lambda: set_all_selection(True)).pack(side='left', padx=5)
tk.Button(frame_action, text="☐ 전체 해제", command=lambda: set_all_selection(False)).pack(side='left', padx=5)

# 실행 버튼
btn_copy = tk.Button(frame_action, text="🚀 체크된 파일 복사하기", command=copy_checked_files, bg="lightblue", font=("맑은 고딕", 10, "bold"))
btn_copy.pack(side='right', padx=5, ipady=5)

# 5. 상태 표시
lbl_status = tk.Label(root, text="대기 중...", bd=1, relief=tk.SUNKEN, anchor='w')
lbl_status.pack(side='bottom', fill='x')

root.mainloop()