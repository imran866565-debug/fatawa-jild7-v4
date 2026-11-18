#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 7 easy-Urdu tashreeh v4 chunks into jild-07.json.

Reads the 15 chunk files listed in chunks-manifest-v4-jild07.json,
concatenates them in order 01 -> 15, derives start_page = min(pages)
where the field is absent, normalises page markers, validates, and
writes {"masail": [...]} to jild-07.json.

ORDER -- chunk order is the order (no quirk, unlike Jild 1 Part 2):
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-07.json
  has ID order == concatenation order of the v4 chunks 01..15 (verified
  locally by the coordinator: all 300 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.

NO RENAME QUIRK in Jild 7: the v3 merged file has 300 UNIQUE ids — the
  book numbers no masala twice in this jild (unlike Jild 5, which had
  two masail 263 and two masail 304, and Jild 6, which had two masail
  774). Chunk ids are used exactly as written; the merge asserts
  duplicate-free ids instead of renaming anything.

START_PAGE: every one of the 15 v4 chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 15 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  300 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-07.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 683 unique pages (min 6, max 721);
  volume_ids == {47}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild7-p6, last id jild7-p720.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild07.json"

# Concatenation order: chunk files 01 -> 15, in order.
CHUNK_ORDER = [f"jild-07-chunk-{n:02d}.json" for n in range(1, 16)]

EXPECTED_ITEMS = 300
EXPECTED_PAGES = 683
EXPECTED_MIN_PAGE = 6
EXPECTED_MAX_PAGE = 721
EXPECTED_VOLUME_IDS = {47}
EXPECTED_FIRST_ID = "jild7-p6"
EXPECTED_LAST_ID = "jild7-p720"

# v3 ID sequence, verbatim from content/tashreeh/jild-07.json.
V3_IDS = ['jild7-p6', 'jild7-p8', 'jild7-masala-846', 'jild7-masala-847', 'jild7-masala-848', 'jild7-masala-849', 'jild7-masala-850', 'jild7-masala-851', 'jild7-masala-855', 'jild7-masala-856', 'jild7-masala-858', 'jild7-p56', 'jild7-masala-859', 'jild7-masala-860', 'jild7-masala-861', 'jild7-masala-862', 'jild7-p106', 'jild7-p109', 'jild7-p112', 'jild7-masala-866', 'jild7-p117', 'jild7-p123', 'jild7-p127', 'jild7-masala-867', 'jild7-masala-868', 'jild7-masala-869', 'jild7-masala-870', 'jild7-p136', 'jild7-masala-871', 'jild7-masala-872', 'jild7-masala-873', 'jild7-masala-876', 'jild7-masala-877', 'jild7-masala-878', 'jild7-p148', 'jild7-masala-879', 'jild7-masala-880', 'jild7-masala-881', 'jild7-masala-882', 'jild7-p156', 'jild7-p159', 'jild7-p161', 'jild7-p163', 'jild7-p165', 'jild7-p168', 'jild7-p171', 'jild7-masala-883', 'jild7-masala-884', 'jild7-masala-885-890', 'jild7-masala-891', 'jild7-masala-892', 'jild7-masala-893', 'jild7-masala-894', 'jild7-masala-896', 'jild7-masala-897', 'jild7-masala-898', 'jild7-masala-899', 'jild7-masala-900', 'jild7-masala-902', 'jild7-masala-903', 'jild7-masala-904', 'jild7-masala-905', 'jild7-masala-906', 'jild7-masala-907', 'jild7-masala-908', 'jild7-masala-909', 'jild7-masala-910', 'jild7-masala-911-922', 'jild7-masala-923', 'jild7-masala-924-927', 'jild7-p206', 'jild7-masala-928', 'jild7-masala-929', 'jild7-masala-930', 'jild7-masala-931', 'jild7-masala-932', 'jild7-masala-933', 'jild7-masala-934', 'jild7-masala-935', 'jild7-masala-936', 'jild7-masala-938', 'jild7-masala-939', 'jild7-masala-940', 'jild7-masala-941', 'jild7-masala-942', 'jild7-masala-943', 'jild7-masala-944', 'jild7-masala-945', 'jild7-masala-946', 'jild7-masala-947', 'jild7-masala-948', 'jild7-masala-949', 'jild7-masala-950', 'jild7-masala-951', 'jild7-masala-952', 'jild7-masala-953', 'jild7-masala-954', 'jild7-masala-955', 'jild7-masala-956', 'jild7-masala-957', 'jild7-masala-958', 'jild7-masala-959', 'jild7-masala-960', 'jild7-masala-961', 'jild7-masala-962', 'jild7-p256', 'jild7-masala-963', 'jild7-masala-964', 'jild7-masala-965', 'jild7-masala-966', 'jild7-masala-967', 'jild7-masala-969', 'jild7-masala-970', 'jild7-masala-971', 'jild7-masala-972', 'jild7-masala-973', 'jild7-masala-975', 'jild7-masala-977', 'jild7-masala-978', 'jild7-masala-979', 'jild7-masala-980', 'jild7-masala-981', 'jild7-masala-982', 'jild7-masala-983', 'jild7-masala-984', 'jild7-masala-985', 'jild7-masala-986', 'jild7-p306', 'jild7-masala-987', 'jild7-masala-990', 'jild7-masala-991', 'jild7-masala-992', 'jild7-masala-993', 'jild7-masala-994', 'jild7-masala-995', 'jild7-masala-996', 'jild7-masala-997', 'jild7-masala-998', 'jild7-masala-999', 'jild7-masala-1000', 'jild7-masala-1002', 'jild7-p356', 'jild7-masala-1003', 'jild7-masala-1004', 'jild7-masala-1005', 'jild7-masala-1006', 'jild7-masala-1007', 'jild7-masala-1008', 'jild7-masala-1009', 'jild7-masala-1010', 'jild7-masala-1011', 'jild7-masala-1017', 'jild7-masala-1018', 'jild7-masala-1019', 'jild7-masala-1020', 'jild7-masala-1021', 'jild7-masala-1022', 'jild7-masala-1023', 'jild7-masala-1024', 'jild7-masala-1025', 'jild7-masala-1026', 'jild7-masala-1027', 'jild7-masala-1028', 'jild7-masala-1029', 'jild7-masala-1030', 'jild7-masala-1031', 'jild7-masala-1032', 'jild7-p406', 'jild7-masala-1033', 'jild7-masala-1034', 'jild7-masala-1036', 'jild7-masala-1037', 'jild7-masala-1038', 'jild7-masala-1039', 'jild7-masala-1040', 'jild7-masala-1041', 'jild7-masala-1042', 'jild7-masala-1043', 'jild7-masala-1044', 'jild7-masala-1045', 'jild7-masala-1046', 'jild7-masala-1047', 'jild7-masala-1048', 'jild7-masala-1049', 'jild7-masala-150-155', 'jild7-masala-1056', 'jild7-masala-1057', 'jild7-masala-1058-1059', 'jild7-masala-1060', 'jild7-p456', 'jild7-masala-1061', 'jild7-masala-1062', 'jild7-masala-1063', 'jild7-masala-1064', 'jild7-masala-1065', 'jild7-masala-1066', 'jild7-masala-1069', 'jild7-masala-1070', 'jild7-masala-1071', 'jild7-masala-1072', 'jild7-masala-1073', 'jild7-masala-1074', 'jild7-masala-1075', 'jild7-masala-1076', 'jild7-masala-1077', 'jild7-masala-1078', 'jild7-masala-1079', 'jild7-masala-1080', 'jild7-masala-1081', 'jild7-masala-1082', 'jild7-masala-1083', 'jild7-masala-1084', 'jild7-masala-1085', 'jild7-masala-1086', 'jild7-masala-1087', 'jild7-masala-1088', 'jild7-masala-1089', 'jild7-p506', 'jild7-p507', 'jild7-p509', 'jild7-p510', 'jild7-p512', 'jild7-p514', 'jild7-p516', 'jild7-p521', 'jild7-p524', 'jild7-masala-1096', 'jild7-masala-1097', 'jild7-masala-1098', 'jild7-masala-1099', 'jild7-masala-1100', 'jild7-masala-1103', 'jild7-masala-1104', 'jild7-masala-1106', 'jild7-masala-1107', 'jild7-masala-1107b', 'jild7-masala-1108', 'jild7-masala-1109', 'jild7-p556', 'jild7-masala-1110', 'jild7-masala-1111', 'jild7-masala-1112', 'jild7-masala-1113', 'jild7-p606', 'jild7-p608', 'jild7-p610', 'jild7-p613', 'jild7-p615', 'jild7-p616', 'jild7-p618', 'jild7-p620', 'jild7-p621', 'jild7-p623', 'jild7-p625', 'jild7-p627', 'jild7-p629', 'jild7-p631', 'jild7-p633', 'jild7-p634', 'jild7-p636', 'jild7-p638', 'jild7-p639', 'jild7-p641', 'jild7-p643', 'jild7-p645', 'jild7-p646', 'jild7-p648', 'jild7-p651', 'jild7-p653', 'jild7-p656', 'jild7-p658', 'jild7-masala-1114', 'jild7-p662', 'jild7-p664', 'jild7-p666', 'jild7-p668', 'jild7-p670', 'jild7-p672', 'jild7-p674', 'jild7-p676', 'jild7-p678', 'jild7-p680', 'jild7-p682', 'jild7-p684', 'jild7-p686', 'jild7-p688', 'jild7-p690', 'jild7-p692', 'jild7-p694', 'jild7-p696', 'jild7-p698', 'jild7-p700', 'jild7-p702', 'jild7-p704', 'jild7-p706', 'jild7-p708', 'jild7-p711', 'jild7-p714', 'jild7-p717', 'jild7-p720']

# v3 pages per item id, verbatim from content/tashreeh/jild-07.json.
V3_PAGES = {
"jild7-p6": [6, 7],
"jild7-p8": [8, 9],
"jild7-masala-846": [38, 39],
"jild7-masala-847": [39, 40],
"jild7-masala-848": [40, 41],
"jild7-masala-849": [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
"jild7-masala-850": [52, 53],
"jild7-masala-851": [53],
"jild7-masala-855": [53, 54],
"jild7-masala-856": [54],
"jild7-masala-858": [55],
"jild7-p56": [56, 57, 58],
"jild7-masala-859": [59, 60],
"jild7-masala-860": [59, 60],
"jild7-masala-861": [61, 62, 63, 64],
"jild7-masala-862": [66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105],
"jild7-p106": [106, 107, 108],
"jild7-p109": [109, 110, 111],
"jild7-p112": [112, 113],
"jild7-masala-866": [114, 115, 116],
"jild7-p117": [117, 118, 119, 120, 121, 122],
"jild7-p123": [123, 124, 125, 126],
"jild7-p127": [127, 128, 129, 130],
"jild7-masala-867": [130, 131],
"jild7-masala-868": [131, 132],
"jild7-masala-869": [132, 133],
"jild7-masala-870": [133, 134, 135],
"jild7-p136": [136, 137, 138],
"jild7-masala-871": [138],
"jild7-masala-872": [138, 139, 140],
"jild7-masala-873": [141, 142],
"jild7-masala-876": [142, 143, 144],
"jild7-masala-877": [144, 145],
"jild7-masala-878": [145, 146, 147],
"jild7-p148": [148, 149, 150],
"jild7-masala-879": [150, 151],
"jild7-masala-880": [151, 152],
"jild7-masala-881": [152, 153],
"jild7-masala-882": [153, 154, 155],
"jild7-p156": [156, 157, 158],
"jild7-p159": [159, 160],
"jild7-p161": [161, 162],
"jild7-p163": [163, 164],
"jild7-p165": [165, 166, 167],
"jild7-p168": [168, 169, 170],
"jild7-p171": [171, 172],
"jild7-masala-883": [173, 174],
"jild7-masala-884": [175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186],
"jild7-masala-885-890": [186, 187, 188, 189, 190, 191, 192],
"jild7-masala-891": [192],
"jild7-masala-892": [192, 193],
"jild7-masala-893": [193],
"jild7-masala-894": [193, 194],
"jild7-masala-896": [194],
"jild7-masala-897": [194, 195],
"jild7-masala-898": [195],
"jild7-masala-899": [195],
"jild7-masala-900": [195, 196],
"jild7-masala-902": [196, 197],
"jild7-masala-903": [197],
"jild7-masala-904": [197, 198],
"jild7-masala-905": [198],
"jild7-masala-906": [198],
"jild7-masala-907": [198, 199],
"jild7-masala-908": [199],
"jild7-masala-909": [199, 200],
"jild7-masala-910": [200],
"jild7-masala-911-922": [200, 201, 202],
"jild7-masala-923": [202, 203, 204, 205],
"jild7-masala-924-927": [205],
"jild7-p206": [206],
"jild7-masala-928": [206, 207],
"jild7-masala-929": [207],
"jild7-masala-930": [207, 208],
"jild7-masala-931": [208],
"jild7-masala-932": [208],
"jild7-masala-933": [208, 209],
"jild7-masala-934": [209, 210],
"jild7-masala-935": [210, 211, 212, 213, 214],
"jild7-masala-936": [214, 215, 216, 217, 218],
"jild7-masala-938": [219],
"jild7-masala-939": [219],
"jild7-masala-940": [219, 220, 221, 222, 223, 224, 225, 226],
"jild7-masala-941": [226, 227, 228, 229],
"jild7-masala-942": [229, 230],
"jild7-masala-943": [230],
"jild7-masala-944": [231, 232],
"jild7-masala-945": [232],
"jild7-masala-946": [232, 233],
"jild7-masala-947": [234, 235],
"jild7-masala-948": [235, 236],
"jild7-masala-949": [236],
"jild7-masala-950": [237],
"jild7-masala-951": [237, 238],
"jild7-masala-952": [238],
"jild7-masala-953": [238, 239],
"jild7-masala-954": [240, 241, 242],
"jild7-masala-955": [242, 243],
"jild7-masala-956": [243, 244],
"jild7-masala-957": [244, 245, 246, 247, 249],
"jild7-masala-958": [250, 251],
"jild7-masala-959": [251, 252],
"jild7-masala-960": [253],
"jild7-masala-961": [254, 255],
"jild7-masala-962": [255],
"jild7-p256": [256, 257, 258],
"jild7-masala-963": [258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270],
"jild7-masala-964": [270, 271, 272, 273, 274, 275],
"jild7-masala-965": [275, 276, 277, 278, 279],
"jild7-masala-966": [280],
"jild7-masala-967": [280, 281, 282, 283, 284, 285, 286],
"jild7-masala-969": [287, 288, 289],
"jild7-masala-970": [289, 291],
"jild7-masala-971": [291, 292],
"jild7-masala-972": [292, 293, 294, 295, 296, 297],
"jild7-masala-973": [297],
"jild7-masala-975": [298, 299],
"jild7-masala-977": [299],
"jild7-masala-978": [299, 300],
"jild7-masala-979": [300],
"jild7-masala-980": [300, 301],
"jild7-masala-981": [301, 302],
"jild7-masala-982": [302],
"jild7-masala-983": [302],
"jild7-masala-984": [302],
"jild7-masala-985": [302],
"jild7-masala-986": [302, 303, 304, 305],
"jild7-p306": [306],
"jild7-masala-987": [306, 307],
"jild7-masala-990": [307, 308],
"jild7-masala-991": [308, 309],
"jild7-masala-992": [310],
"jild7-masala-993": [310, 311, 312],
"jild7-masala-994": [312, 313],
"jild7-masala-995": [313, 314],
"jild7-masala-996": [314, 315, 316, 317, 318],
"jild7-masala-997": [318, 319],
"jild7-masala-998": [319],
"jild7-masala-999": [319, 320, 321],
"jild7-masala-1000": [322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355],
"jild7-masala-1002": [355],
"jild7-p356": [356, 357],
"jild7-masala-1003": [357, 358],
"jild7-masala-1004": [358, 359],
"jild7-masala-1005": [359, 360, 361],
"jild7-masala-1006": [361, 362],
"jild7-masala-1007": [362, 363],
"jild7-masala-1008": [363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384],
"jild7-masala-1009": [385],
"jild7-masala-1010": [385],
"jild7-masala-1011": [385, 386],
"jild7-masala-1017": [386, 387, 388],
"jild7-masala-1018": [388, 389],
"jild7-masala-1019": [389, 390],
"jild7-masala-1020": [390],
"jild7-masala-1021": [391, 392, 393],
"jild7-masala-1022": [393, 394],
"jild7-masala-1023": [394],
"jild7-masala-1024": [394, 395],
"jild7-masala-1025": [395],
"jild7-masala-1026": [395, 396],
"jild7-masala-1027": [396, 397],
"jild7-masala-1028": [398],
"jild7-masala-1029": [398, 399],
"jild7-masala-1030": [399, 400],
"jild7-masala-1031": [401],
"jild7-masala-1032": [401, 402, 403, 404, 405],
"jild7-p406": [406, 407, 408, 409, 410, 411],
"jild7-masala-1033": [411, 412, 413, 414, 415, 416, 417],
"jild7-masala-1034": [417, 418, 419, 420],
"jild7-masala-1036": [420],
"jild7-masala-1037": [420, 421, 422],
"jild7-masala-1038": [422],
"jild7-masala-1039": [422, 423],
"jild7-masala-1040": [423, 424, 425],
"jild7-masala-1041": [425, 426],
"jild7-masala-1042": [426],
"jild7-masala-1043": [427, 428, 429, 430],
"jild7-masala-1044": [430, 431, 432, 433, 434, 435, 436, 437, 438],
"jild7-masala-1045": [438, 439, 440, 441, 442, 443],
"jild7-masala-1046": [443, 444],
"jild7-masala-1047": [444, 445],
"jild7-masala-1048": [445, 446],
"jild7-masala-1049": [446, 447],
"jild7-masala-150-155": [447, 448, 449],
"jild7-masala-1056": [449],
"jild7-masala-1057": [449, 450],
"jild7-masala-1058-1059": [450, 451, 452, 453, 454, 455],
"jild7-masala-1060": [455],
"jild7-p456": [456],
"jild7-masala-1061": [456, 457],
"jild7-masala-1062": [458, 459],
"jild7-masala-1063": [459, 460],
"jild7-masala-1064": [460],
"jild7-masala-1065": [460, 461],
"jild7-masala-1066": [461, 462, 463, 464],
"jild7-masala-1069": [464, 465],
"jild7-masala-1070": [465, 466, 467, 468],
"jild7-masala-1071": [468],
"jild7-masala-1072": [469],
"jild7-masala-1073": [469, 470],
"jild7-masala-1074": [470, 471],
"jild7-masala-1075": [471, 472],
"jild7-masala-1076": [472, 473],
"jild7-masala-1077": [473, 474],
"jild7-masala-1078": [474, 475],
"jild7-masala-1079": [475],
"jild7-masala-1080": [475, 476],
"jild7-masala-1081": [476, 477, 478, 479, 480, 481],
"jild7-masala-1082": [482, 483],
"jild7-masala-1083": [483, 484],
"jild7-masala-1084": [484, 485],
"jild7-masala-1085": [485],
"jild7-masala-1086": [485],
"jild7-masala-1087": [485],
"jild7-masala-1088": [487],
"jild7-masala-1089": [488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505],
"jild7-p506": [506, 507],
"jild7-p507": [507, 508],
"jild7-p509": [509, 510],
"jild7-p510": [510, 511],
"jild7-p512": [512, 513],
"jild7-p514": [514, 515, 516],
"jild7-p516": [516, 517, 518, 519, 520, 521],
"jild7-p521": [521, 522, 523, 524],
"jild7-p524": [524, 525, 526],
"jild7-masala-1096": [526, 527, 528],
"jild7-masala-1097": [528, 529],
"jild7-masala-1098": [528, 529],
"jild7-masala-1099": [529, 530],
"jild7-masala-1100": [530, 531],
"jild7-masala-1103": [531, 532],
"jild7-masala-1104": [531, 532, 533, 534, 535],
"jild7-masala-1106": [535, 536, 537, 538, 539, 540],
"jild7-masala-1107": [540, 541, 542, 543, 544],
"jild7-masala-1107b": [544],
"jild7-masala-1108": [544, 545, 546],
"jild7-masala-1109": [546, 547, 548, 549, 550, 551, 552, 553, 554, 555],
"jild7-p556": [556],
"jild7-masala-1110": [556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568],
"jild7-masala-1111": [568, 569],
"jild7-masala-1112": [569],
"jild7-masala-1113": [570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605],
"jild7-p606": [606, 607],
"jild7-p608": [608, 609],
"jild7-p610": [610, 611, 612],
"jild7-p613": [613, 614],
"jild7-p615": [615],
"jild7-p616": [616, 617],
"jild7-p618": [618, 619],
"jild7-p620": [620],
"jild7-p621": [621, 622],
"jild7-p623": [623, 624],
"jild7-p625": [625, 626],
"jild7-p627": [627, 628],
"jild7-p629": [629, 630],
"jild7-p631": [631],
"jild7-p633": [633],
"jild7-p634": [634, 635],
"jild7-p636": [636, 637],
"jild7-p638": [638],
"jild7-p639": [639, 640],
"jild7-p641": [641, 642],
"jild7-p643": [643, 644],
"jild7-p645": [645],
"jild7-p646": [646, 647],
"jild7-p648": [648, 649, 650],
"jild7-p651": [651, 652],
"jild7-p653": [653, 654, 655],
"jild7-p656": [656, 657],
"jild7-p658": [658, 659],
"jild7-masala-1114": [660, 661],
"jild7-p662": [662, 663],
"jild7-p664": [664, 665],
"jild7-p666": [666, 667],
"jild7-p668": [668, 669],
"jild7-p670": [670, 671],
"jild7-p672": [672, 673],
"jild7-p674": [674, 675],
"jild7-p676": [676, 677],
"jild7-p678": [678, 679],
"jild7-p680": [680, 681],
"jild7-p682": [682, 683],
"jild7-p684": [684, 685],
"jild7-p686": [686, 687],
"jild7-p688": [688, 689],
"jild7-p690": [690, 691],
"jild7-p692": [692, 693],
"jild7-p694": [694, 695],
"jild7-p696": [696, 697],
"jild7-p698": [698, 699],
"jild7-p700": [700, 701],
"jild7-p702": [702, 703],
"jild7-p704": [704, 705],
"jild7-p706": [706, 707],
"jild7-p708": [708, 709, 710],
"jild7-p711": [711, 712, 713],
"jild7-p714": [714, 715, 716],
"jild7-p717": [717, 718, 719],
"jild7-p720": [720, 721],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 15, f"expected 15 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (chunks 06, 12).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO RENAME QUIRK in Jild 7: the v3 merged file has 300 UNIQUE
    # ids — the book numbers no masala twice in this jild. Chunk ids
    # are used exactly as written.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS before validation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 7)")

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-07.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-07.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
