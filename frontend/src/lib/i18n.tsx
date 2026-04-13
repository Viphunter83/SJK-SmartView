"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Language = 'vi' | 'en';

type Translations = {
  [key: string]: string;
};

const dictionaries: Record<Language, Translations> = {
  vi: {
    // Common
    loading: "Đang tải...",
    error: "Lỗi",
    success: "Thành công",
    manager: "Quản lý:",
    logout: "Đăng xuất",
    logging_out: "Đang đăng xuất...",
    cancel: "Hủy",
    next: "Tiếp tục",
    back: "Quay lại",
    delete: "Xóa",

    // Auth
    login_title: "SJK SmartView",
    login_subtitle: "Đăng nhập hệ thống quản lý quảng cáo",
    email_label: "EMAIL",
    email_placeholder: "name@shojiki.vn",
    password_label: "MẬT KHẨU",
    login_button: "Đăng nhập vào hệ thống",
    login_loading: "Đang xác thực...",
    login_corp_access: "Truy cập doanh nghiệp Shojiki",
    err_invalid_cred: "Email hoặc mật khẩu không hợp lệ",
    err_too_many_req: "Quá nhiều yêu cầu. Vui lòng thử lại sau",
    err_network: "Lỗi đăng nhập. Kiểm tra kết nối của bạn",

    // Sidebar
    screen_catalog: "Danh mục màn hình",
    street_upload: "Tải lên từ đường phố",
    mockup_history: "Lịch sử Mockup",
    location_map: "Bản đồ địa điểm",

    // Catalog
    catalog_title: "Chọn bảng quảng cáo",
    search_placeholder: "Tìm theo vị trí hoặc tên...",
    all_locations: "Tất cả địa điểm",
    screens: "màn hình",
    select_banner: "Chọn banner này",
    format: "Định dạng:",
    no_locations_found: "Không tìm thấy địa điểm",
    try_another_search: "Thử tìm kiếm khác",

    // Map
    map_select_location: "Chọn màn hình này",

    // Mockup History
    history_title: "Lịch sử Mockup",
    status_completed: "Hoàn thành",
    status_failed: "Thất bại",
    status_processing: "Đang xử lý",
    location: "Vị trí",
    processing_time: "Thời gian tạo",
    sec: "giây",
    date: "Ngày",
    delete_confirm: "Bạn có chắc chắn muốn xóa mockup này?",
    download_result: "Tải kết quả",
    download_primary: "Cơ bản",
    download_creative: "Tải ảnh gốc",
    no_history: "Chưa có mockup nào được tạo",

    // Mockup Creator
    creator_title: "Trình tạo Mockup Màn Hình",
    step_1: "Nền",
    step_2: "Góc",
    step_3: "Thiết kế",
    step_4: "Đã xong",
    upload_drag_bg: "Kéo & thả ảnh nền màn hình",
    or_click: "hoặc click để chọn",
    bg_custom_desc: "Ảnh đường phố có màn hình nơi kết quả sẽ được chèn vào.",
    bg_catalog_desc: "Ảnh nền đã được chọn sẵn từ danh mục.",
    bg_uploaded: "Ảnh nền đã được tải lên",
    change_photo: "Đổi ảnh",
    auto_detect_corners: "Tự động nhận diện góc",
    move_corners_desc: "Di chuyển các điểm xanh để đánh dấu 4 góc của màn hình. Kết quả sẽ tự động điều chỉnh theo phối cảnh.",
    upload_drag_creative: "Kéo & thả ảnh thiết kế (quảng cáo)",
    creative_desc: "Ảnh này sẽ được chèn vào khu vực màn hình đã chọn.",
    creative_uploaded: "Thiết kế đã tải lên",
    render_button: "Tạo Mockup",
    rendering: "Đang tạo...",
    generating_cloud: "Đang tạo trên GPU đám mây...",
    download_mockup: "Tải Mockup",
    start_new: "Tạo mới",
    err_bg_required: "Vui lòng cung cấp ảnh nền",
    err_creative_required: "Vui lòng cung cấp ảnh thiết kế",
    ratio: "Tỷ lệ"
  },
  en: {
    // Common
    loading: "Loading...",
    error: "Error",
    success: "Success",
    manager: "Manager:",
    logout: "Logout",
    logging_out: "Logging out...",
    cancel: "Cancel",
    next: "Next",
    back: "Back",
    delete: "Delete",

    // Auth
    login_title: "SJK SmartView",
    login_subtitle: "Log in to ad management system",
    email_label: "EMAIL",
    email_placeholder: "name@shojiki.vn",
    password_label: "PASSWORD",
    login_button: "Log into the system",
    login_loading: "Authenticating...",
    login_corp_access: "Shojiki Corporate Access",
    err_invalid_cred: "Invalid email or password",
    err_too_many_req: "Too many requests. Try again later",
    err_network: "Login error. Check your connection",

    // Sidebar
    screen_catalog: "Screen Catalog",
    street_upload: "Street Upload",
    mockup_history: "Mockup History",
    location_map: "Location Map",

    // Catalog
    catalog_title: "Select a Billboard",
    search_placeholder: "Search by location or name...",
    all_locations: "All locations",
    screens: "screens",
    select_banner: "Select this banner",
    format: "Format:",
    no_locations_found: "No locations found",
    try_another_search: "Try another search",

    // Map
    map_select_location: "Select this screen",

    // Mockup History
    history_title: "Mockup History",
    status_completed: "Completed",
    status_failed: "Failed",
    status_processing: "Processing",
    location: "Location",
    processing_time: "Processing time",
    sec: "sec",
    date: "Date",
    delete_confirm: "Are you sure you want to delete this mockup?",
    download_result: "Download result",
    download_primary: "Primary",
    download_creative: "Download creative",
    no_history: "No mockups generated yet",

    // Mockup Creator
    creator_title: "Screen Mockup Creator",
    step_1: "Bg",
    step_2: "Corners",
    step_3: "Creative",
    step_4: "Done",
    upload_drag_bg: "Drag & drop screen background",
    or_click: "or click to select",
    bg_custom_desc: "The street photo with the screen where the result will be inserted.",
    bg_catalog_desc: "Background image is pre-selected from the catalog.",
    bg_uploaded: "Background uploaded",
    change_photo: "Change photo",
    auto_detect_corners: "Auto-detect corners",
    move_corners_desc: "Move the blue points to mark the 4 corners of the screen. The result will be adjusted automatically.",
    upload_drag_creative: "Drag & drop your creative (ad) design",
    creative_desc: "This image will be inserted into the selected screen area.",
    creative_uploaded: "Creative uploaded",
    render_button: "Generate Mockup",
    rendering: "Generating...",
    generating_cloud: "Generating on Cloud GPU...",
    download_mockup: "Download Mockup",
    start_new: "Start New",
    err_bg_required: "Please provide a background image",
    err_creative_required: "Please provide a creative image",
    ratio: "Ratio"
  }
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>('vi');
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    const savedLang = localStorage.getItem('sjk-lang') as Language;
    if (savedLang && (savedLang === 'vi' || savedLang === 'en')) {
      setLanguageState(savedLang);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('sjk-lang', lang);
  };

  const t = (key: string): string => {
    // Always fallback to the key itself if not found
    return dictionaries[language][key] || dictionaries['en'][key] || key;
  };

  // Prevent hydration mismatch by avoiding rendering until client mounts
  // Although context provider doesn't render raw DOM, it's safer.
  
  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
