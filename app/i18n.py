from typing import Optional, Dict
from jinja2 import pass_context

JA_TRANSLATIONS: Dict[str, str] = {
    # Header & Navigation
    "Sign In": "サインイン",
    "Sign Out": "サインアウト",
    "My Account": "マイアカウント",
    "Catalog": "カタログ",
    "Search or ask AI...": "検索またはAIに質問...",
    "Search": "検索",
    "Return to Main Menu": "メインメニューに戻る",
    "Fish": "魚",
    "Dogs": "犬",
    "Reptiles": "爬虫類",
    "Cats": "猫",
    "Birds": "鳥",

    # Cart
    "Shopping Cart": "ショッピングカート",
    "Item ID": "商品ID",
    "Product ID": "製品ID",
    "Description": "説明",
    "In Stock?": "在庫あり?",
    "Quantity": "数量",
    "List Price": "定価",
    "Total Cost": "合計金額",
    "Remove": "削除",
    "Sub Total:": "小計:",
    "Update Cart": "カート更新",
    "Your cart is empty.": "カートは空です。",
    "Proceed to Checkout": "チェックアウトに進む",
    "Pet Favorites": "お気に入りのペット",
    "Shop for more of your favorite pets here.": "お気に入りのペットをここでお買い物できます。",

    # Account
    "User ID:": "ユーザーID:",
    "New password:": "新しいパスワード:",
    "Repeat password:": "パスワード再入力:",
    "User Information": "ユーザー情報",
    "Account Information": "アカウント情報",
    "Profile Information": "プロフィール情報",
    "First name:": "名:",
    "Last name:": "姓:",
    "Email:": "メールアドレス:",
    "Phone:": "電話番号:",
    "Address 1:": "住所1:",
    "Address 2:": "住所2:",
    "City:": "市区町村:",
    "State:": "都道府県/州:",
    "Zip:": "郵便番号:",
    "Country:": "国:",
    "Language Preference:": "言語設定:",
    "Favourite Category:": "お気に入りカテゴリー:",
    "Enable MyList": "マイリストを有効にする",
    "Enable MyBanner": "マイバナーを有効にする",
    "Save Account Information": "アカウント情報を保存",
    "My Orders": "注文履歴",
    "User Registration": "新規ユーザー登録",
    "Edit Account": "アカウント編集",

    # Orders & Checkout
    "Payment Details": "お支払い情報",
    "Billing Address": "請求先住所",
    "Shipping Address": "お届け先住所",
    "Ship to different address...": "別の住所へ配送...",
    "Order": "注文",
    "Order #": "注文番号 #",
    "Order Date": "注文日",
    "Status": "ステータス",
    "Courier:": "配送業者:",
    "Card Type:": "カード種別:",
    "Card Number:": "カード番号:",
    "Expiry Date (MM/YYYY):": "有効期限 (MM/YYYY):",
    "Continue": "次へ進む",
    "Confirm Order": "注文確認",
    "Please confirm the information below and then submit...": "以下の内容をご確認の上、送信してください...",
    "Submit": "注文を確定する",
    "Thank you, your order has been submitted.": "ご注文ありがとうございました。注文が完了しました。",
    "Order Details": "注文詳細",

    # Catalog & Products
    "Product": "商品",
    "Name": "名称",
    "Items": "アイテム一覧",
    "Item": "アイテム",
    "Price": "価格",
    "Add to Cart": "カートに追加",
    "Back": "戻る",
    "Semantic Search": "セマンティック検索",

    # AI Advisor
    "AI Pet Advisor": "AIペットアドバイザー",
    "Smart Pet Advisor": "スマートペットアドバイザー",
    "Ask": "質問する",
    "Ask about pet care or diet...": "ペットのケアや食事について質問..."
}

def translate_text(text: str, lang: Optional[str] = "english") -> str:
    if lang and lang.lower() == "japanese":
        return JA_TRANSLATIONS.get(text, text)
    return text

@pass_context
def t_context(context: dict, text: str, lang: Optional[str] = None) -> str:
    if not lang:
        user = context.get("user")
        if not user:
            request = context.get("request")
            if request and hasattr(request, "session"):
                user = request.session.get("user")
        if isinstance(user, dict):
            lang = user.get("langpref", "english")
        else:
            lang = "english"
    return translate_text(text, lang)
