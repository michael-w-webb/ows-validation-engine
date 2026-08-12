



# Commented out b/c Microsoft disabled filtering capability through the url

# """
# Automate Power BI:
# - Load Org values from cc_file_directory.py or gjc_file_metadata_directory.py (keys of dict; spaces→underscores)
# - For each Org: open report filtered via URL
# - Apply Round Numbers filter (UI_Specs/[Round Numbers] = True/False) to URL
# - Open Filters pane, hide page tabs, hide service header
# - Screenshot the report iframe cleanly
# - Build a PPT with full-bleed slides (one per Org per Grant), plus a title slide
# - If running both grants, produce two PPTs (one per Grant)

# Prereqs:
#     pip install selenium python-pptx Pillow

# Author: M365 Copilot
# """

# import os
# import re
# import time
# from datetime import datetime
# from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
# import importlib.util

# from selenium import webdriver
# from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.edge.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # --- PPT dependencies ---
# from pptx import Presentation
# from pptx.util import Inches, Pt
# from PIL import Image

# # ----------------------------
# # ARGS (NEW)
# # ----------------------------
# GRANT_LIST = ['Career ConneCT', 'Good Jobs Challenge']
# GRANT_LOOP = 'Career ConneCT'  # 'All' | 'Career ConneCT' | 'Good Jobs Challenge'
# Round_Numbers = True  # True | False — filter UI_Specs/[Round Numbers] in report URL

# # ----------------------------
# # CONFIG
# # ----------------------------
# EDGE_DRIVER_PATH = r"C:\Users\DalyRob\Downloads\edgedriver_win64_1\msedgedriver.exe"

# # Base report URLs per Grant (update GJC if different)
# # "https://app.powerbigov.us/groups/57ba19a1-f62c-40d5-a043-67dbd430e612/reports/b5553d70-6809-49c3-9e26-a4b31880bae2/053e1fa8226709d017a4"
# POWERBI_URL_BASE_CC = ("https://app.powerbigov.us/groups/57ba19a1-f62c-40d5-a043-67dbd430e612/reports/87fc2fbd-cd9c-4b79-8641-0faf650413bd/a02732781befb7b1f1e9")
# POWERBI_URL_BASE_GJC = POWERBI_URL_BASE_CC  # TODO: set to GJC report URL if different

# POWERBI_URL_BASES = {
#     'Career ConneCT': POWERBI_URL_BASE_CC,
#     'Good Jobs Challenge': POWERBI_URL_BASE_GJC,
# }

# # Folder to save PPT & screenshots
# PPT_DIR = r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\Power BI\Reports"
# PPT_TITLE = "DemographicDataPPT"  # We'll append the Grant name to the file name below
# SCREENSHOT_DIR = os.path.join(PPT_DIR, "Screenshots")

# # Dict modules (in the SAME folder as THIS script)
# CC_FILE_NAME = "applications/career_connect_grantee_sheets/file_directory.py"
# CC_DICT_NAME = "file_directory"  # dict whose KEYS are the org names

# GJC_FILE_NAME = "gjc_file_metadata_directory.py"
# GJC_DICT_NAME = "submission_files"  # dict whose KEYS are the org names for GJC

# try:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# except NameError:
#     BASE_DIR = os.getcwd()
# CC_FILE_PATH = os.path.join(BASE_DIR, CC_FILE_NAME)
# GJC_FILE_PATH = os.path.join(BASE_DIR, GJC_FILE_NAME)

# # Power BI filter column info
# ORG_TABLE = "Dim_Sector,Grantee,Goals"
# ORG_COLUMN = "Org"

# # Grant filter (same Query3_participant table)
# GRANT_COLUMN = "Grant"

# # Normalize display grant name to dataset value used in Power BI (adjust if needed)
# GRANT_VALUE_URL_MAP = {
#     'Career ConneCT': 'Career Connect',  # stylized display name → dataset value
#     'Good Jobs Challenge': 'Good Jobs Challenge',
# }
# def grant_filter_value_for_powerbi(grant: str) -> str:
#     return GRANT_VALUE_URL_MAP.get(grant, grant)

# # Round Numbers filter column info
# ROUND_TABLE = "UI_Specs"
# ROUND_COLUMN = "Round Numbers"

# # Delay to let the report render after navigation
# WAIT_FOR_RENDER_SECONDS = 6  # adjust if needed

# # Target viewport size for consistent screenshots
# VIEWPORT_WIDTH = 1920
# VIEWPORT_HEIGHT = 1080

# # ----------------------------
# # HELPERS: URL & values
# # ----------------------------
# def ensure_folder(path: str):
#     os.makedirs(path, exist_ok=True)

# def safe_filter_value_from_key(key: str) -> str:
#     """
#     Convert a dictionary key to a Power BI filter value:
#       - Trim
#       - Replace any whitespace with underscore
#       - Collapse multiple underscores
#     Example: "Ability Beyond" -> "Ability_Beyond"
#     """
#     k = key.strip()
#     k = re.sub(r"\s+", "_", k)     # whitespace → underscore
#     k = re.sub(r"_+", "_", k)      # collapse multiple underscores
#     return k

# def safe_filename_from_value(value: str) -> str:
#     """
#     Create a filesystem-safe filename component from a filter value.
#     Keep alphanumerics, underscore, hyphen; convert others to underscore.
#     """
#     value = value or "All"
#     name = re.sub(r"[^\w\-]+", "_", value)
#     name = re.sub(r"_+", "_", name).strip("_")
#     return name[:120]

# def load_org_values_from_dict_file(module_path: str, dict_name: str) -> list:
#     """
#     Import a dict from the given module path and read keys.
#     Convert each key to a filter-safe value (spaces → underscores).
#     Returns a de-duplicated list of filter values preserving order.
#     """
#     if not os.path.exists(module_path):
#         print(f"⚠️ File not found: {module_path}")
#         return []

#     try:
#         spec = importlib.util.spec_from_file_location(dict_name, module_path)
#         module = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(module)
#     except Exception as e:
#         print(f"⚠️ Error importing {module_path}: {e}")
#         return []

#     if not hasattr(module, dict_name):
#         print(f"⚠️ '{dict_name}' not found in {module_path}.")
#         return []

#     data_dict = getattr(module, dict_name)
#     if not isinstance(data_dict, dict):
#         print(f"⚠️ '{dict_name}' is not a dict in {module_path}.")
#         return []

#     keys = list(data_dict.keys())
#     values = [safe_filter_value_from_key(k) for k in keys if isinstance(k, str) and k.strip()]
#     # De-duplicate while preserving order
#     seen = set()
#     ordered_unique = []
#     for v in values:
#         if v not in seen:
#             seen.add(v)
#             ordered_unique.append(v)

#     print(f"✅ Loaded {len(ordered_unique)} Org values from {os.path.basename(module_path)} ({dict_name})")
#     return ordered_unique

# def _format_filter_expr(table: str, column: str, value) -> str:
#     """
#     Format a single Power BI URL filter expression: Table/Column eq <value>
#     - Strings are quoted with single quotes (internal single quotes doubled)
#     - Booleans -> true/false (unquoted)
#     - Numbers -> unquoted
#     - None or '' -> return '' (caller should skip)
#     """
#     if value is None or (isinstance(value, str) and value.strip() == ""):
#         return ""
#     if isinstance(value, bool):
#         return f"{table}/{column} eq {'true' if value else 'false'}"
#     if isinstance(value, (int, float)):
#         return f"{table}/{column} eq {value}"
#     # String
#     safe_value = str(value).replace("'", "''")
#     return f"{table}/{column} eq '{safe_value}'"

# def build_filtered_url(base_url: str, table: str, column: str, value, extra_filters=None) -> str:
#     """
#     Build a Power BI URL with filters.
#     - The primary filter (table/column/value) is typically Org.
#     - extra_filters: list of (table, column, value), e.g., Grant and Round Numbers.
#     RULES:
#       * Multiple filters for the SAME table are combined into a single expression using 'and'
#         e.g., filter=Query3_participant/Grant eq 'Career Connect' and Query3_participant/Org eq 'EWIB'
#       * Filters for DIFFERENT tables are sent as separate &filter= parameters
#         e.g., &filter=UI_Specs/Round Numbers eq true
#     """
#     parts = urlparse(base_url)
#     qs = parse_qs(parts.query, keep_blank_values=True)

#     # Collect conditions by table
#     table_to_exprs = {}

#     def add_condition(t: str, c: str, v):
#         expr = _format_filter_expr(t, c, v)
#         if expr:
#             table_to_exprs.setdefault(t, []).append(expr)

#     # Primary filter (e.g., Org)
#     add_condition(table, column, value)

#     # Extra filters (e.g., Grant, Round Numbers)
#     if extra_filters:
#         for (t, c, v) in extra_filters:
#             add_condition(t, c, v)

#     # Build filter params: one entry per table; join same-table expressions with ' and '
#     filter_params = []
#     for t, exprs in table_to_exprs.items():
#         if not exprs:
#             continue
#         if len(exprs) == 1:
#             filter_params.append(exprs[0])
#         else:
#             filter_params.append(" and ".join(exprs))

#     if filter_params:
#         qs["filter"] = filter_params

#     new_query = urlencode(qs, doseq=True)
#     return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, new_query, parts.fragment))

# # ----------------------------
# # HELPERS: View & DOM tweaks
# # ----------------------------
# def set_consistent_viewport(driver, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT):
#     """Set a predictable viewport size so screenshots are uniform."""
#     try:
#         driver.set_window_size(width, height)
#         time.sleep(0.3)
#     except Exception:
#         pass

# def wait_for_powerbi_iframe(driver, timeout=10):
#     """
#     Wait until the Power BI report iframe appears.
#     Returns the iframe WebElement or None.
#     """
#     try:
#         iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
#             By.XPATH, "//iframe[contains(@src,'powerbi')]"
#         )))
#         return iframe
#     except Exception:
#         return None

# def open_filters_pane_host(driver, timeout=5) -> bool:
#     """
#     Click the host 'Filters' toggle button (outside the iframe) to show the Filters pane.
#     This avoids deep iframe interactions.
#     """
#     try:
#         btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((
#             By.XPATH, "//button[contains(@aria-label,'Filters') or contains(@title,'Filters')]"
#         )))
#         btn.click()
#         time.sleep(0.4)
#         return True
#     except Exception:
#         return False

# def hide_service_header(driver):
#     """
#     Hide the top service header that contains 'File Export Share Get insights'.
#     We attempt multiple CSS selectors to be resilient to DOM changes.
#     """
#     selectors = [
#         "[role='menubar']",
#         "div[aria-label*='Report header']",
#         "div[class*='CommandBar']",
#         "div.ms-CommandBar",
#         "header",
#         "[role='toolbar']",
#         "div[class*='header']",
#         "div[class*='appBar']",
#     ]
#     js = """
#     var sels = arguments[0];
#     sels.forEach(function(sel){
#         try {
#             var el = document.querySelector(sel);
#             if (el) { el.style.display = 'none'; }
#         } catch(e) {}
#     });
#     """
#     try:
#         driver.execute_script(js, selectors)
#         time.sleep(0.2)
#     except Exception:
#         pass

# def hide_page_navigation_in_iframe(driver, timeout=8):
#     """
#     Hide page tabs/navigation inside the report iframe.
#     Switch into the iframe, run CSS to hide tablist/nav pane, then switch back.
#     """
#     iframe = wait_for_powerbi_iframe(driver, timeout=timeout)
#     if not iframe:
#         return False

#     try:
#         driver.execute_script("arguments[0].scrollIntoView({block:'center'});", iframe)
#         time.sleep(0.2)
#         driver.switch_to.frame(iframe)
#         selectors = [
#             "[role='tablist']",
#             "div[class*='tabBar']",
#             "div[class*='pagesPane']",
#             "div[aria-label*='Pages pane']",
#             "div[class*='navContentPane']",
#             "div[id*='ReportPagesNavigation']",
#         ]
#         js = """
#         var sels = arguments[0];
#         sels.forEach(function(sel){
#             try {
#                 var el = document.querySelector(sel);
#                 if (el) { el.style.display = 'none'; }
#             } catch(e) {}
#         });
#         """
#         driver.execute_script(js, selectors)
#         time.sleep(0.2)
#     except Exception:
#         pass
#     finally:
#         try:
#             driver.switch_to.default_content()
#         except Exception:
#             pass
#     return True

# def go_full_screen(driver, timeout=WAIT_FOR_RENDER_SECONDS):
#     """
#     Enter full screen:
#     1) Browser maximize via driver.fullscreen_window()
#     2) Fallback Ctrl+Shift+F
#     """
#     wait = WebDriverWait(driver, timeout)

#     try:
#         driver.fullscreen_window()
#         time.sleep(0.6)
#         return True  # Maximizes the browser window which can help with screenshot quality.
#     except Exception:
#         pass

#     # Fallback keyboard shortcut
#     try:
#         actions = ActionChains(driver)
#         actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('f') \
#                .key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
#         time.sleep(0.6)
#         return True
#     except Exception:
#         pass

#     return False

# # ----------------------------
# # HELPERS: Screenshots & PPT
# # ----------------------------
# def capture_report_iframe_screenshot(driver, path, timeout=8) -> bool:
#     """
#     Capture ONLY the Power BI report iframe rectangle for a clean image.
#     This avoids the top service header and browser chrome.
#     """
#     try:
#         iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
#             By.XPATH, "//iframe[contains(@src,'powerbi')]"
#         )))
#         driver.execute_script("arguments[0].scrollIntoView({block:'center'});", iframe)
#         time.sleep(0.25)
#         iframe.screenshot(path)
#         return True
#     except Exception:
#         return False

# def capture_viewport_screenshot(driver, path) -> bool:
#     """Fallback to a standard viewport screenshot."""
#     try:
#         return driver.save_screenshot(path)
#     except Exception:
#         return False

# def make_ppt_full_bleed(ppt_filename: str, image_paths: list, title_text: str):
#     """
#     Create a PPT:
#       - Title slide
#       - One full-bleed slide per image
#     Slide size matches the first image dimensions.
#     """
#     if not image_paths:
#         print("No images to include in PPT.")
#         return

#     with Image.open(image_paths[0]) as img:
#         w_px, h_px = img.size
#         # Default to 96 DPI if not present
#         dpi_x, dpi_y = img.info.get("dpi", (96, 96))
#         dpi_x = dpi_x if isinstance(dpi_x, (int, float)) and dpi_x > 0 else 96
#         dpi_y = dpi_y if isinstance(dpi_y, (int, float)) and dpi_y > 0 else 96
#         w_in = w_px / dpi_x
#         h_in = h_px / dpi_y

#     prs = Presentation()
#     prs.slide_width = Inches(w_in)
#     prs.slide_height = Inches(h_in)

#     # Title slide
#     title_slide = prs.slides.add_slide(prs.slide_layouts[0])
#     title_shape = title_slide.shapes.title
#     title_shape.text = title_text
#     title_shape.text_frame.paragraphs[0].font.size = Pt(44)

#     # Image slides
#     for img_path in image_paths:
#         slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
#         slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width, height=prs.slide_height)

#     prs.save(ppt_filename)
#     print(f"📄 PPT created with {len(image_paths)} image slides: {ppt_filename}")

# # ----------------------------
# # MAIN
# # ----------------------------
# def main():
#     ensure_folder(PPT_DIR)
#     ensure_folder(SCREENSHOT_DIR)

#     # Prepare Selenium (once; reuse driver across grants)
#     opts = Options()
#     opts.add_argument("--start-maximized")
#     # Improve HiDPI consistency
#     opts.add_argument("--force-device-scale-factor=1")

#     service = EdgeService(executable_path=EDGE_DRIVER_PATH)
#     driver = webdriver.Edge(service=service, options=opts)

#     print("🌐 Edge opened.")

#     # Determine which grants to run
#     if GRANT_LOOP == 'All':
#         selected_grants = GRANT_LIST
#     elif GRANT_LOOP in GRANT_LIST:
#         selected_grants = [GRANT_LOOP]
#     else:
#         print(f"⚠️ GRANT_LOOP value '{GRANT_LOOP}' not recognized; defaulting to 'All'.")
#         selected_grants = GRANT_LIST

#     for grant in selected_grants:
#         print("\n" + "="*80)
#         print(f"🚀 Running grant: {grant} (Round Numbers = {Round_Numbers})")
#         print("="*80)

#         base_url = POWERBI_URL_BASES.get(grant, POWERBI_URL_BASE_CC)

#         # Load Org values per grant
#         if grant == 'Career ConneCT':
#             org_values = load_org_values_from_dict_file(CC_FILE_PATH, CC_DICT_NAME)
#         else:
#             org_values = load_org_values_from_dict_file(GJC_FILE_PATH, GJC_DICT_NAME)

#         # If none found, proceed with just the 'All' (unfiltered Org) view
#         if not org_values:
#             print("⚠️ No Org values found; proceeding with 'All' only.")
#             org_values = []

#         # Per-grant screenshot collection
#         screenshot_paths = []

#         # Always run first pass unfiltered (None sentinel), then each org filtered
#         run_list = [None] + org_values

#         for idx, org_value in enumerate(run_list, start=1):
#             label_for_log = "All" if not org_value else org_value
#             print(f"\n[{idx}/{len(run_list)}] {grant} → Org: {label_for_log}")

#             # Build URL with Org + Grant (same table, combined with 'and') + Round Numbers (separate)
#             filtered_url = build_filtered_url(
#                 base_url,
#                 ORG_TABLE,
#                 ORG_COLUMN,
#                 org_value,
#                 extra_filters=[
#                     (ORG_TABLE, GRANT_COLUMN, grant_filter_value_for_powerbi(grant)),
#                     (ROUND_TABLE, ROUND_COLUMN, Round_Numbers)
#                 ]
#             )
#             print("URL =", filtered_url)

#             driver.get(filtered_url)
#             # Give the report time to render
#             time.sleep(WAIT_FOR_RENDER_SECONDS)

#             # Consistent viewport
#             set_consistent_viewport(driver, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT)

#             # Hide service header (File/Export/Share/Get insights)
#             hide_service_header(driver)

#             # Hide page navigation inside the iframe
#             hide_page_navigation_in_iframe(driver)

#             # Try entering full screen
#             fs_ok = go_full_screen(driver, timeout=WAIT_FOR_RENDER_SECONDS)
#             if fs_ok:
#                 print("🖥️ Entered full screen.")
#             else:
#                 print("⚠️ Full screen attempt did not succeed (continuing).")

#             time.sleep(0.6)  # settle a moment

#             grant_safe = safe_filename_from_value(grant)
#             safe_name = safe_filename_from_value(org_value if org_value else "All")
#             screenshot_path = os.path.join(
#                 SCREENSHOT_DIR,
#                 f"{PPT_TITLE}_{grant_safe}_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
#             )

#             # Prefer iframe-only screenshot (clean report area); fallback to viewport
#             ok = capture_report_iframe_screenshot(driver, screenshot_path, timeout=8)
#             if not ok:
#                 ok = capture_viewport_screenshot(driver, screenshot_path)

#             if ok:
#                 print("🖼️ Saved:", screenshot_path)
#                 screenshot_paths.append(screenshot_path)
#             else:
#                 print("❌ Failed to capture screenshot.")

#             time.sleep(0.4)

#         # Build per-grant PPT (file name includes grant name)
#         if screenshot_paths:
#             grant_safe = safe_filename_from_value(grant)
#             ppt_filename = os.path.join(
#                 PPT_DIR,
#                 f"{PPT_TITLE}_{grant_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
#             )
#             title_text = f"{PPT_TITLE} – {grant} (Round Numbers = {Round_Numbers})"
#             make_ppt_full_bleed(ppt_filename, screenshot_paths, title_text)
#         else:
#             print(f"⚠️ No screenshots captured for {grant}; PPT will not be created.")

#     input("Press Enter to close the browser...")
#     try:
#         driver.quit()
#     except Exception:
#         pass

# if __name__ == "__main__":
#     main()