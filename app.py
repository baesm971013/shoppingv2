import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict

# 페이지 설정
st.set_page_config(
    page_title="쇼핑몰 관리 시스템",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 파일 경로
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "items.json")

def init_data_dir():
    """데이터 디렉토리 초기화"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_items() -> List[Dict]:
    """아이템 데이터 로드"""
    init_data_dir()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_items(items: List[Dict]):
    """아이템 데이터 저장"""
    init_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def get_next_id(items: List[Dict]) -> int:
    """다음 ID 생성"""
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1

# 세션 상태 초기화
if 'items' not in st.session_state:
    st.session_state.items = load_items()
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = "id"
if 'filter_category' not in st.session_state:
    st.session_state.filter_category = "전체"

# 헤더
st.title("🛒 쇼핑몰 관리 시스템")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("📋 메뉴")
    
    menu = st.radio(
        "기능 선택",
        ["아이템 조회", "아이템 추가", "아이템 수정", "아이템 삭제", "통계 정보"],
        index=0
    )
    
    st.markdown("---")
    
    # 검색 및 필터
    st.subheader("🔍 검색 및 필터")
    st.session_state.search_query = st.text_input("아이템 검색", value=st.session_state.search_query)
    
    # 카테고리 필터
    categories = ["전체"] + sorted(list(set(item.get('category', '기타') for item in st.session_state.items)))
    st.session_state.filter_category = st.selectbox("카테고리 필터", categories, index=0 if st.session_state.filter_category == "전체" else categories.index(st.session_state.filter_category) if st.session_state.filter_category in categories else 0)
    
    # 정렬 옵션
    st.session_state.sort_by = st.selectbox(
        "정렬 기준",
        ["id", "이름", "가격 (낮은순)", "가격 (높은순)", "재고 (낮은순)", "재고 (높은순)"],
        index=0 if st.session_state.sort_by == "id" else ["id", "이름", "가격 (낮은순)", "가격 (높은순)", "재고 (낮은순)", "재고 (높은순)"].index(st.session_state.sort_by) if st.session_state.sort_by in ["id", "이름", "가격 (낮은순)", "가격 (높은순)", "재고 (낮은순)", "재고 (높은순)"] else 0
    )

# 메인 컨텐츠
if menu == "아이템 조회":
    st.header("📦 아이템 리스트")
    
    # 필터링 및 정렬
    filtered_items = st.session_state.items.copy()
    
    # 검색 필터
    if st.session_state.search_query:
        filtered_items = [
            item for item in filtered_items
            if st.session_state.search_query.lower() in item.get('name', '').lower() or
               st.session_state.search_query.lower() in item.get('description', '').lower()
        ]
    
    # 카테고리 필터
    if st.session_state.filter_category != "전체":
        filtered_items = [
            item for item in filtered_items
            if item.get('category', '기타') == st.session_state.filter_category
        ]
    
    # 정렬
    if st.session_state.sort_by == "이름":
        filtered_items.sort(key=lambda x: x.get('name', ''))
    elif st.session_state.sort_by == "가격 (낮은순)":
        filtered_items.sort(key=lambda x: float(x.get('price', 0)))
    elif st.session_state.sort_by == "가격 (높은순)":
        filtered_items.sort(key=lambda x: float(x.get('price', 0)), reverse=True)
    elif st.session_state.sort_by == "재고 (낮은순)":
        filtered_items.sort(key=lambda x: int(x.get('stock', 0)))
    elif st.session_state.sort_by == "재고 (높은순)":
        filtered_items.sort(key=lambda x: int(x.get('stock', 0)), reverse=True)
    else:  # id
        filtered_items.sort(key=lambda x: int(x.get('id', 0)))
    
    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("전체 아이템 수", len(st.session_state.items))
    with col2:
        st.metric("필터된 아이템 수", len(filtered_items))
    with col3:
        total_value = sum(float(item.get('price', 0)) * int(item.get('stock', 0)) for item in st.session_state.items)
        st.metric("총 재고 가치", f"{total_value:,.0f}원")
    with col4:
        total_stock = sum(int(item.get('stock', 0)) for item in st.session_state.items)
        st.metric("총 재고 수", total_stock)
    
    st.markdown("---")
    
    # 아이템 표시
    if filtered_items:
        for item in filtered_items:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.subheader(f"🛍️ {item.get('name', '이름 없음')}")
                    st.caption(f"ID: {item.get('id', 'N/A')} | 카테고리: {item.get('category', '기타')}")
                    if item.get('description'):
                        st.write(item.get('description'))
                with col2:
                    st.metric("가격", f"{float(item.get('price', 0)):,.0f}원")
                with col3:
                    stock = int(item.get('stock', 0))
                    stock_color = "normal" if stock > 10 else "inverse" if stock > 0 else "off"
                    st.metric("재고", stock, delta=None)
                with col4:
                    st.write(f"등록일: {item.get('created_at', 'N/A')}")
                st.markdown("---")
    else:
        st.info("표시할 아이템이 없습니다.")

elif menu == "아이템 추가":
    st.header("➕ 아이템 추가")
    
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("아이템 이름 *", placeholder="예: 노트북")
        description = st.text_area("설명", placeholder="아이템에 대한 상세 설명을 입력하세요")
        category = st.text_input("카테고리", placeholder="예: 전자제품", value="기타")
        price = st.number_input("가격 (원) *", min_value=0, value=0, step=1000)
        stock = st.number_input("재고 수량 *", min_value=0, value=0, step=1)
        
        submitted = st.form_submit_button("아이템 추가", use_container_width=True)
        
        if submitted:
            if name and price >= 0 and stock >= 0:
                new_item = {
                    'id': get_next_id(st.session_state.items),
                    'name': name,
                    'description': description,
                    'category': category if category else "기타",
                    'price': float(price),
                    'stock': int(stock),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.items.append(new_item)
                save_items(st.session_state.items)
                st.success(f"✅ '{name}' 아이템이 성공적으로 추가되었습니다!")
                st.balloons()
            else:
                st.error("❌ 필수 항목(이름, 가격, 재고)을 모두 입력해주세요.")

elif menu == "아이템 수정":
    st.header("✏️ 아이템 수정")
    
    if st.session_state.items:
        item_options = {f"{item.get('id')} - {item.get('name')}": item for item in st.session_state.items}
        selected_key = st.selectbox("수정할 아이템 선택", list(item_options.keys()))
        
        if selected_key:
            selected_item = item_options[selected_key]
            
            with st.form("edit_item_form"):
                st.write(f"**현재 ID:** {selected_item.get('id')}")
                name = st.text_input("아이템 이름 *", value=selected_item.get('name', ''))
                description = st.text_area("설명", value=selected_item.get('description', ''))
                category = st.text_input("카테고리", value=selected_item.get('category', '기타'))
                price = st.number_input("가격 (원) *", min_value=0, value=float(selected_item.get('price', 0)), step=1000)
                stock = st.number_input("재고 수량 *", min_value=0, value=int(selected_item.get('stock', 0)), step=1)
                
                submitted = st.form_submit_button("아이템 수정", use_container_width=True)
                
                if submitted:
                    if name and price >= 0 and stock >= 0:
                        item_id = selected_item.get('id')
                        for i, item in enumerate(st.session_state.items):
                            if item.get('id') == item_id:
                                st.session_state.items[i] = {
                                    'id': item_id,
                                    'name': name,
                                    'description': description,
                                    'category': category if category else "기타",
                                    'price': float(price),
                                    'stock': int(stock),
                                    'created_at': selected_item.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                break
                        save_items(st.session_state.items)
                        st.success(f"✅ '{name}' 아이템이 성공적으로 수정되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 필수 항목(이름, 가격, 재고)을 모두 입력해주세요.")
    else:
        st.info("수정할 아이템이 없습니다.")

elif menu == "아이템 삭제":
    st.header("🗑️ 아이템 삭제")
    
    if st.session_state.items:
        item_options = {f"{item.get('id')} - {item.get('name')}": item for item in st.session_state.items}
        selected_key = st.selectbox("삭제할 아이템 선택", list(item_options.keys()))
        
        if selected_key:
            selected_item = item_options[selected_key]
            
            st.warning("⚠️ 삭제된 아이템은 복구할 수 없습니다!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**아이템 정보:**")
                st.json(selected_item)
            
            with col2:
                st.write("**삭제 확인**")
                if st.button("🗑️ 삭제하기", type="primary", use_container_width=True):
                    item_id = selected_item.get('id')
                    st.session_state.items = [item for item in st.session_state.items if item.get('id') != item_id]
                    save_items(st.session_state.items)
                    st.success(f"✅ '{selected_item.get('name')}' 아이템이 삭제되었습니다!")
                    st.rerun()
    else:
        st.info("삭제할 아이템이 없습니다.")

elif menu == "통계 정보":
    st.header("📊 통계 정보")
    
    if st.session_state.items:
        # 전체 통계
        col1, col2, col3, col4 = st.columns(4)
        
        total_items = len(st.session_state.items)
        total_value = sum(float(item.get('price', 0)) * int(item.get('stock', 0)) for item in st.session_state.items)
        total_stock = sum(int(item.get('stock', 0)) for item in st.session_state.items)
        avg_price = sum(float(item.get('price', 0)) for item in st.session_state.items) / total_items if total_items > 0 else 0
        
        with col1:
            st.metric("전체 아이템 수", total_items)
        with col2:
            st.metric("총 재고 가치", f"{total_value:,.0f}원")
        with col3:
            st.metric("총 재고 수량", total_stock)
        with col4:
            st.metric("평균 가격", f"{avg_price:,.0f}원")
        
        st.markdown("---")
        
        # 카테고리별 통계
        st.subheader("📂 카테고리별 통계")
        categories = {}
        for item in st.session_state.items:
            cat = item.get('category', '기타')
            if cat not in categories:
                categories[cat] = {'count': 0, 'total_value': 0, 'total_stock': 0}
            categories[cat]['count'] += 1
            categories[cat]['total_value'] += float(item.get('price', 0)) * int(item.get('stock', 0))
            categories[cat]['total_stock'] += int(item.get('stock', 0))
        
        if categories:
            cat_data = []
            for cat, stats in categories.items():
                cat_data.append({
                    '카테고리': cat,
                    '아이템 수': stats['count'],
                    '총 가치': f"{stats['total_value']:,.0f}원",
                    '총 재고': stats['total_stock']
                })
            st.dataframe(cat_data, use_container_width=True)
        
        st.markdown("---")
        
        # 재고 부족 아이템
        st.subheader("⚠️ 재고 부족 아이템 (10개 미만)")
        low_stock_items = [item for item in st.session_state.items if int(item.get('stock', 0)) < 10]
        if low_stock_items:
            low_stock_data = []
            for item in low_stock_items:
                low_stock_data.append({
                    'ID': item.get('id'),
                    '이름': item.get('name'),
                    '카테고리': item.get('category', '기타'),
                    '재고': item.get('stock'),
                    '가격': f"{float(item.get('price', 0)):,.0f}원"
                })
            st.dataframe(low_stock_data, use_container_width=True)
        else:
            st.success("✅ 재고 부족 아이템이 없습니다!")
        
        st.markdown("---")
        
        # 최근 추가된 아이템
        st.subheader("🆕 최근 추가된 아이템 (최대 5개)")
        sorted_by_date = sorted(st.session_state.items, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        if sorted_by_date:
            recent_data = []
            for item in sorted_by_date:
                recent_data.append({
                    'ID': item.get('id'),
                    '이름': item.get('name'),
                    '카테고리': item.get('category', '기타'),
                    '가격': f"{float(item.get('price', 0)):,.0f}원",
                    '재고': item.get('stock'),
                    '등록일': item.get('created_at', 'N/A')
                })
            st.dataframe(recent_data, use_container_width=True)
    else:
        st.info("통계를 표시할 아이템이 없습니다.")

# 푸터
st.markdown("---")
st.caption("🛒 쇼핑몰 관리 시스템 v1.0")

