"""
Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
CareerConneCT “training data” workbooks supported by the validation
pipeline. It encodes:

    • Canonical  names used throughout the pipeline  
    • All known spelling / formatting variants (“label maps”) that appear
      in provider-submitted Excel files  
    • -level metadata describing expected types, requirements, and
      accepted categorical responses  
    • Workbook-level structure (sheet names, starting rows/s, and
      schema for both *simple format* and *four-sheet format*)  
    • Logic template phrases used by natural-language rule descriptions  

These definitions serve as the central contract between:

    1. **WorkbookLoader** – to map raw header text → canonical names  
    2. **NormalizationEngine / Type classes** – to validate, clean,
       and coerce  values into standardized formats  
    3. **CrossRuleEngine** – to interpret variable types and retrieve the
       correct pandas Series for cross-sheet logic evaluation  
    4. **UI or reporting layers** – to generate intelligible messages and
       consistent descriptions of rule expectations  

-----------------------------------------------------------------------
Label Maps (“labels”)
-----------------------------------------------------------------------

Each sheet definition includes a mapping:

    {
        "Canonical Name": ["Variant A", "Variant B", ...]
    }

The workbook loader uses these maps to:

    • Match raw  headers from provider files  
    • Normalize them into predictable, canonical field names  
    • Tolerate typos, punctuation differences, capitalization,
      OWS-specific export labels, and Salesforce-style field names  

These maps are *lossless*: they never drop fields, they only expand the
set of acceptable  headers.

-----------------------------------------------------------------------
Accepted Responses and Types (“accepted_responses_w_types”)
-----------------------------------------------------------------------

Each canonical  has a metadata block describing:

    • type – one of the defined  classes
      (e.g., "dateTime", "categorical", "boolean", "identifier",
      "hourlyWage", "hoursWorked", "stateID7", "CIPCode", "ONETCode")

    • required – whether the field must be present and non-blank

    • accepted_responses – (optional) list of canonical categorical
      values used by categorical normalization and by
      CrossRuleEngine for logical operations

These definitions are consumed by:

    • Base subclasses during normalization  
    • CrossRuleEngine.get_variable() when creating Variable instances  
    • Rule authoring and error-message templates  

-----------------------------------------------------------------------
Workbook Structure (“workbook_definitions”)
-----------------------------------------------------------------------

The outer `workbook_definitions` object organizes schemas by:

    workbook_type → workbook_format → sheet_name → sheet_definition

For example:

    "training data" →
        "simple format" →
            "Report" → {labels, accepted_responses, starting_row, ...}

        "four sheet format" →
            "Personal Information"
            "Training"
            "Credential"
            "Outcomes"

Each sheet definition includes:

    • labels – a full header normalization map  
    • accepted_responses – the  metadata schema  
    • starting_row – where data begins (allows skipping header clutter)  
    • starting_ – permits partial-sheet ingestion  
    • s_used – reserved for restricting the importable subset

This structure makes it easy for the loader to select the correct
parsing logic depending on which workbook format the provider uploaded.

-----------------------------------------------------------------------
Logic Templates and Expectations
-----------------------------------------------------------------------

Two auxiliary dictionaries define natural-language templates used by
`CrossRuleEngine.describe_logic()`:

    • Logic_Templates – maps operator categories to English snippets
      (e.g., “is in the past”, “is blank”, “is {values}”)

    • Logic_Expectations – indicates whether a field is “required” or
      “should be blank” in IF/THEN constructions

These templates ensure that every rule written in clause-tree syntax can
be rendered into a readable English explanation without custom text.

-----------------------------------------------------------------------
Extending or Updating This Module
-----------------------------------------------------------------------

To add new fields or update schemas:

    1. Add new label variants under the correct sheet’s `labels` dict  
    2. Add (or update) a canonical entry under `accepted_responses`
       with its correct type and accepted categorical responses  
    3. If a new sheet or workbook format is added, create a new
       nested dictionary under `workbook_definitions` following the
       established pattern  
    4. If a new variable type is introduced (e.g., NAICSCode),
       ensure that Base+Variable subclasses support the type
       before referencing it here  

All changes propagate automatically through:

    •  mapping  
    • Data normalization  
    • Cross-sheet rule evaluation  
    • Validation reporting  

This module is therefore the **single source of truth** for schema
consistency across every component of the CareerConneCT validation
pipeline.
"""

# 0) Accepted Response Mappings { user_friendly_name: { accepted_response: [variants] } }
CT_TOWN_MAPPING = {
  "Abington": [
    "Abington", "Abington, Connecticut", "Abington, CT", "Abington CT",
    "06230"
  ],
  "Allingtown": [
    "Allingtown", "Allingtown, Connecticut", "Allingtown, CT", "Allingtown CT",
    "06516"
  ],
  "Amston": [
    "Amston", "Amston, Connecticut", "Amston, CT", "Amston CT",
    "06231"
  ],
  "Ansonia": [
    "Ansonia", "Ansonia, Connecticut", "Ansonia, CT", "Ansonia CT",
    "06401"
  ],
  "Ashford": [
    "Ashford", "Ashford, Connecticut", "Ashford, CT", "Ashford CT",
    "06250", "06278",
    "0901501430"
  ],
  "Avon": [
    "Avon", "Avon, Connecticut", "Avon, CT", "Avon CT",
    "06001",
    "0900302060", "004"
  ],
  "Baltic": [
    "Baltic", "Baltic, Connecticut", "Baltic, CT", "Baltic CT",
    "06330"
  ],
  "Ballouville": [
    "Ballouville", "Ballouville, Connecticut", "Ballouville, CT", "Ballouville CT",
    "06233"
  ],
  "Bantam": [
    "Bantam", "Bantam, Connecticut", "Bantam, CT", "Bantam CT",
    "06750"
  ],
  "Barkhamsted": [
    "Barkhamsted", "Barkhamsted, Connecticut", "Barkhamsted, CT", "Barkhamsted CT",
    "06063",
    "0900502760", "005"
  ],
  "Beacon Falls": [
    "Beacon Falls", "Beacon Falls, Connecticut", "Beacon Falls, CT", "Beacon Falls CT",
    "06403",
    "0900903250", "006"
  ],
  "Berlin": [
    "Berlin", "Berlin, Connecticut", "Berlin, CT", "Berlin CT",
    "06037",
    "0900304300", "007"
  ],
  "Bethany": [
    "Bethany", "Bethany, Connecticut", "Bethany, CT", "Bethany CT",
    "06524",
    "0900904580", "008"
  ],
  "Bethlehem": [
    "Bethlehem", "Bethlehem, Connecticut", "Bethlehem, CT", "Bethlehem CT",
    "06751",
    "0900504930", "010"
  ],
  "Bloomfield": [
    "Bloomfield", "Bloomfield, Connecticut", "Bloomfield, CT", "Bloomfield CT",
    "06002",
    "0900305910", "011"
  ],
  "Bolton": [
    "Bolton", "Bolton, Connecticut", "Bolton, CT", "Bolton CT",
    "06043",
    "0901306260", "012"
  ],
  "Bozrah": [
    "Bozrah", "Bozrah, Connecticut", "Bozrah, CT", "Bozrah CT",
    "06334",
    "0901106820", "013"
  ],
  "Branford": [
    "Branford", "Branford, Connecticut", "Branford, CT", "Branford CT",
    "06405",
    "0900907310", "014"
  ],
  "Bridgeport": [
    "Bridgeport", "Bridgeport, Connecticut", "Bridgeport, CT", "Bridgeport CT",
    "06601", "06602", "06604", "06605", "06606", "06607", "06608", "06610", "06611", "06612",
    "06650", "06673", "06699",
    "0900108070", "015"
  ],
  "Bridgewater": [
    "Bridgewater", "Bridgewater, Connecticut", "Bridgewater, CT", "Bridgewater CT",
    "06752",
    "0900508210", "016"
  ],
  "Bristol": [
    "Bristol", "Bristol, Connecticut", "Bristol, CT", "Bristol CT",
    "06010", "06011",
    "0900308490", "017"
  ],
  "Broad Brook": [
    "Broad Brook", "Broad Brook, Connecticut", "Broad Brook, CT", "Broad Brook CT",
    "06016"
  ],
  "Brookfield": [
    "Brookfield", "Brookfield, Connecticut", "Brookfield, CT", "Brookfield CT",
    "06804",
    "0900108980", "018"
  ],
  "Brookfield Center": [
    "Brookfield Center", "Brookfield Center, Connecticut", "Brookfield Center, CT", "Brookfield Center CT",
    "06804"
  ],
  "Brooklyn": [
    "Brooklyn", "Brooklyn, Connecticut", "Brooklyn, CT", "Brooklyn CT",
    "06234",
    "0901509190", "019"
  ],
  "Burlington": [
    "Burlington", "Burlington, Connecticut", "Burlington, CT", "Burlington CT",
    "06013", "06085",
    "0900310100", "020"
  ],
  "Canaan": [
    "Canaan", "Canaan, Connecticut", "Canaan, CT", "Canaan CT",
    "06018", "06031",
    "0900510940", "021"
  ],
  "Canterbury": [
    "Canterbury", "Canterbury, Connecticut", "Canterbury, CT", "Canterbury CT",
    "06331",
    "0901512130", "022"
  ],
  "Canton": [
    "Canton", "Canton, Connecticut", "Canton, CT", "Canton CT",
    "06019",
    "0900312270", "023"
  ],
  "Canton Center": [
    "Canton Center", "Canton Center, Connecticut", "Canton Center, CT", "Canton Center CT",
    "06020"
  ],
  "Centerbrook": [
    "Centerbrook", "Centerbrook, Connecticut", "Centerbrook, CT", "Centerbrook CT",
    "06409"
  ],
  "Central Village": [
    "Central Village", "Central Village, Connecticut", "Central Village, CT", "Central Village CT",
    "06332"
  ],
  "Chaplin": [
    "Chaplin", "Chaplin, Connecticut", "Chaplin, CT", "Chaplin CT",
    "06235",
    "0901513810", "024"
  ],
  "Cheshire": [
    "Cheshire", "Cheshire, Connecticut", "Cheshire, CT", "Cheshire CT",
    "06410", "06411", "06408",
    "0900914160", "025"
  ],
  "Chester": [
    "Chester", "Chester, Connecticut", "Chester, CT", "Chester CT",
    "06412",
    "0900714300", "026"
  ],
  "Chesterfield": [
    "Chesterfield", "Chesterfield, Connecticut", "Chesterfield, CT", "Chesterfield CT",
    "06370"
  ],
  "Clinton": [
    "Clinton", "Clinton, Connecticut", "Clinton, CT", "Clinton CT",
    "06413",
    "0900715350", "027"
  ],
  "Cobalt": [
    "Cobalt", "Cobalt, Connecticut", "Cobalt, CT", "Cobalt CT",
    "06414"
  ],
  "Colchester": [
    "Colchester", "Colchester, Connecticut", "Colchester, CT", "Colchester CT",
    "06415", "06420",
    "0901115910", "028"
  ],
  "Colebrook": [
    "Colebrook", "Colebrook, Connecticut", "Colebrook, CT", "Colebrook CT",
    "06021",
    "0900516050", "029"
  ],
  "Collinsville": [
    "Collinsville", "Collinsville, Connecticut", "Collinsville, CT", "Collinsville CT",
    "06022"
  ],
  "Columbia": [
    "Columbia", "Columbia, Connecticut", "Columbia, CT", "Columbia CT",
    "06237",
    "0901316400", "030"
  ],
  "Cos Cob": [
    "Cos Cob", "Cos Cob, Connecticut", "Cos Cob, CT", "Cos Cob CT",
    "06807"
  ],
  "Coventry": [
    "Coventry", "Coventry, Connecticut", "Coventry, CT", "Coventry CT",
    "06238",
    "0901317800", "032"
  ],
  "Cromwell": [
    "Cromwell", "Cromwell, Connecticut", "Cromwell, CT", "Cromwell CT",
    "06416",
    "0900718080", "033"
  ],
  "Danbury": [
    "Danbury", "Danbury, Connecticut", "Danbury, CT", "Danbury CT",
    "06810", "06811", "06812", "06813", "06814", "06816", "06817",
    "0900118500"
  ],
  "Danielson": [
    "Danielson", "Danielson, Connecticut", "Danielson, CT", "Danielson CT",
    "06239"
  ],
  "Darien": [
    "Darien", "Darien, Connecticut", "Darien, CT", "Darien CT",
    "06820",
    "0900118850", "035"
  ],
  "Dayville": [
    "Dayville", "Dayville, Connecticut", "Dayville, CT", "Dayville CT",
    "06241"
  ],
  "Deep River": [
    "Deep River", "Deep River, Connecticut", "Deep River, CT", "Deep River CT",
    "06417",
    "0900719130", "036"
  ],
  "Derby": [
    "Derby", "Derby, Connecticut", "Derby, CT", "Derby CT",
    "06418",
    "0900919550", "037"
  ],
  "Durham": [
    "Durham", "Durham, Connecticut", "Durham, CT", "Durham CT",
    "06422",
    "0900720810", "038"
  ],
  "East Berlin": [
    "East Berlin", "East Berlin, Connecticut", "East Berlin, CT", "East Berlin CT",
    "06023"
  ],
  "East Canaan": [
    "East Canaan", "East Canaan, Connecticut", "East Canaan, CT", "East Canaan CT",
    "06024"
  ],
  "East Glastonbury": [
    "East Glastonbury", "East Glastonbury, Connecticut", "East Glastonbury, CT", "East Glastonbury CT",
    "06025"
  ],
  "East Granby": [
    "East Granby", "East Granby, Connecticut", "East Granby, CT", "East Granby CT",
    "06026",
    "0900322070", "040"
  ],
  "East Haddam": [
    "East Haddam", "East Haddam, Connecticut", "East Haddam, CT", "East Haddam CT",
    "06423",
    "0900722280", "041"
  ],
  "East Hampton": [
    "East Hampton", "East Hampton, Connecticut", "East Hampton, CT", "East Hampton CT",
    "06424",
    "0900722490", "042"
  ],
  "East Hartford": [
    "East Hartford", "East Hartford, Connecticut", "East Hartford, CT", "East Hartford CT",
    "06108", "06118", "06128", "06138",
    "0900322630", "043"
  ],
  "East Hartland": [
    "East Hartland", "East Hartland, Connecticut", "East Hartland, CT", "East Hartland CT",
    "06027"
  ],
  "East Haven": [
    "East Haven", "East Haven, Connecticut", "East Haven, CT", "East Haven CT",
    "06512", "06513",
    "0900922910", "044"
  ],
  "East Killingly": [
    "East Killingly", "East Killingly, Connecticut", "East Killingly, CT", "East Killingly CT",
    "06243"
  ],
  "East Lyme": [
    "East Lyme", "East Lyme, Connecticut", "East Lyme, CT", "East Lyme CT",
    "06333",
    "0901123400", "045"
  ],
  "East Putnam": [
    "East Putnam", "East Putnam, Connecticut", "East Putnam, CT", "East Putnam CT",
    "06260"
  ],
  "East Thompson": [
    "East Thompson", "East Thompson, Connecticut", "East Thompson, CT", "East Thompson CT",
    "06277"
  ],
  "East Willington": [
    "East Willington", "East Willington, Connecticut", "East Willington, CT", "East Willington CT",
    "06279"
  ],
  "East Windsor": [
    "East Windsor", "East Windsor, Connecticut", "East Windsor, CT", "East Windsor CT",
    "06016", "06088",
    "0900324800", "047"
  ],
  "East Windsor Hill": [
    "East Windsor Hill", "East Windsor Hill, Connecticut", "East Windsor Hill, CT", "East Windsor Hill CT",
    "06028"
  ],
  "Ellington": [
    "Ellington", "Ellington, Connecticut", "Ellington, CT", "Ellington CT",
    "06029",
    "0901325360", "048"
  ],
  "Elmwood": [
    "Elmwood", "Elmwood, Connecticut", "Elmwood, CT", "Elmwood CT",
    "06110"
  ],
  "Enfield": [
    "Enfield", "Enfield, Connecticut", "Enfield, CT", "Enfield CT",
    "06082", "06083",
    "0900325990", "049"
  ],
  "Essex": [
    "Essex", "Essex, Connecticut", "Essex, CT", "Essex CT",
    "06426",
    "0900726270", "050"
  ],
  "Falls Village": [
    "Falls Village", "Falls Village, Connecticut", "Falls Village, CT", "Falls Village CT",
    "06031"
  ],
  "Fairfield": [
    "Fairfield", "Fairfield, Connecticut", "Fairfield, CT", "Fairfield CT",
    "06430", "06431", "06432", "06824", "06825",
    "0900126620", "051"
  ],
  "Farmington": [
    "Farmington", "Farmington, Connecticut", "Farmington, CT", "Farmington CT",
    "06030", "06032", "06034", "06085",
    "0900327600", "052"
  ],
  "Fenwick": [
    "Fenwick", "Fenwick, Connecticut", "Fenwick, CT", "Fenwick CT",
    "06475"
  ],
  "Fitchville": [
    "Fitchville", "Fitchville, Connecticut", "Fitchville, CT", "Fitchville CT",
    "06334"
  ],
  "Forestville": [
    "Forestville", "Forestville, Connecticut", "Forestville, CT", "Forestville CT",
    "06010"
  ],
  "Franklin": [
    "Franklin", "Franklin, Connecticut", "Franklin, CT", "Franklin CT",
    "06254",
    "0901129910", "053"
  ],
  "Gales Ferry": [
    "Gales Ferry", "Gales Ferry, Connecticut", "Gales Ferry, CT", "Gales Ferry CT",
    "06335", "06339"
  ],
  "Gaylordsville": [
    "Gaylordsville", "Gaylordsville, Connecticut", "Gaylordsville, CT", "Gaylordsville CT",
    "06755"
  ],
  "Georgetown": [
    "Georgetown", "Georgetown, Connecticut", "Georgetown, CT", "Georgetown CT",
    "06829"
  ],
  "Glasgo": [
    "Glasgo", "Glasgo, Connecticut", "Glasgo, CT", "Glasgo CT",
    "06337"
  ],
  "Glastonbury": [
    "Glastonbury", "Glastonbury, Connecticut", "Glastonbury, CT", "Glastonbury CT",
    "06033",
    "0900331240", "054"
  ],
  "Goshen": [
    "Goshen", "Goshen, Connecticut", "Goshen, CT", "Goshen CT",
    "06756",
    "0900532290", "055"
  ],
  "Granby": [
    "Granby", "Granby, Connecticut", "Granby, CT", "Granby CT",
    "06035", "06090",
    "0900332640", "056"
  ],
  "Greens Farms": [
    "Greens Farms", "Greens Farms, Connecticut", "Greens Farms, CT", "Greens Farms CT",
    "06436"
  ],
  "Griswold": [
    "Griswold", "Griswold, Connecticut", "Griswold, CT", "Griswold CT",
    "06351",
    "0901133900", "058"
  ],
  "Groton": [
    "Groton", "Groton, Connecticut", "Groton, CT", "Groton CT",
    "06340", "06349",
    "0901134250", "059"
  ],
  "Groton Long Point": [
    "Groton Long Point", "Groton Long Point, Connecticut", "Groton Long Point, CT", "Groton Long Point CT",
    "06340"
  ],
  "Guilford": [
    "Guilford", "Guilford, Connecticut", "Guilford, CT", "Guilford CT",
    "06437",
    "0900934950", "060"
  ],
  "Haddam": [
    "Haddam", "Haddam, Connecticut", "Haddam, CT", "Haddam CT",
    "06438",
    "0900735230", "061"
  ],
  "Haddam Neck": [
    "Haddam Neck", "Haddam Neck, Connecticut", "Haddam Neck, CT", "Haddam Neck CT",
    "06424"
  ],
  "Hadlyme": [
    "Hadlyme", "Hadlyme, Connecticut", "Hadlyme, CT", "Hadlyme CT",
    "06439"
  ],
  "Hamden": [
    "Hamden", "Hamden, Connecticut", "Hamden, CT", "Hamden CT",
    "06514", "06517", "06518",
    "0900935650", "062"
  ],
  "Hamburg": [
    "Hamburg", "Hamburg, Connecticut", "Hamburg, CT", "Hamburg CT",
    "06371"
  ],
  "Hampton": [
    "Hampton", "Hampton, Connecticut", "Hampton, CT", "Hampton CT",
    "06247",
    "0901536000", "063"
  ],
  "Hartford": [
    "Hartford", "Hartford, Connecticut", "Hartford, CT", "Hartford CT",
    "06101", "06102", "06103", "06104", "06105", "06106", "06107", "06108",
    "06109", "06110", "06111", "06112", "06114", "06115", "06117", "06118",
    "06119", "06120", "06123", "06126", "06127", "06132", "06133", "06134",
    "06137", "06140", "06141", "06142", "06143", "06144", "06145", "06146",
    "06147", "06150", "06151", "06152", "06153", "06154", "06155", "06156",
    "06160", "06161", "06167", "06176", "06180", "06183", "06199",
    "0900337070", "064"
  ],
  "Harwinton": [
    "Harwinton", "Harwinton, Connecticut", "Harwinton, CT", "Harwinton CT",
    "06791",
    "0900537280", "066"
  ],
  "Hawleyville": [
    "Hawleyville", "Hawleyville, Connecticut", "Hawleyville, CT", "Hawleyville CT",
    "06440"
  ],
  "Hebron": [
    "Hebron", "Hebron, Connecticut", "Hebron, CT", "Hebron CT",
    "06248",
    "0901337910", "067"
  ],
  "Higganum": [
    "Higganum", "Higganum, Connecticut", "Higganum, CT", "Higganum CT",
    "06441"
  ],
  "Huntington": [
    "Huntington", "Huntington, Connecticut", "Huntington, CT", "Huntington CT",
    "06484"
  ],
  "Ivoryton": [
    "Ivoryton", "Ivoryton, Connecticut", "Ivoryton, CT", "Ivoryton CT",
    "06442"
  ],
  "Jewett City": [
    "Jewett City", "Jewett City, Connecticut", "Jewett City, CT", "Jewett City CT",
    "06351"
  ],
  "Kensington": [
    "Kensington", "Kensington, Connecticut", "Kensington, CT", "Kensington CT",
    "06037"
  ],
  "Kent": [
    "Kent", "Kent, Connecticut", "Kent, CT", "Kent CT",
    "06757",
    "0900540290", "068"
  ],
  "Killingly": [
    "Killingly", "Killingly, Connecticut", "Killingly, CT", "Killingly CT",
    "06239",
    "0901540500", "069"
  ],
  "Killingworth": [
    "Killingworth", "Killingworth, Connecticut", "Killingworth, CT", "Killingworth CT",
    "06419",
    "0900740710", "070"
  ],
  "Lake Garda": [
    "Lake Garda", "Lake Garda, Connecticut", "Lake Garda, CT", "Lake Garda CT",
    "06085"
  ],
  "Lakeville": [
    "Lakeville", "Lakeville, Connecticut", "Lakeville, CT", "Lakeville CT",
    "06039"
  ],
  "Lakeside": [
    "Lakeside", "Lakeside, Connecticut", "Lakeside, CT", "Lakeside CT",
    "06758"
  ],
  "Lebanon": [
    "Lebanon", "Lebanon, Connecticut", "Lebanon, CT", "Lebanon CT",
    "06249",
    "0901142390", "071"
  ],
  "Ledyard": [
    "Ledyard", "Ledyard, Connecticut", "Ledyard, CT", "Ledyard CT",
    "06339",
    "0901142600", "072"
  ],
  "Lisbon": [
    "Lisbon", "Lisbon, Connecticut", "Lisbon, CT", "Lisbon CT",
    "06351",
    "0901143230", "073"
  ],
  "Litchfield": [
    "Litchfield", "Litchfield, Connecticut", "Litchfield, CT", "Litchfield CT",
    "06750", "06759",
    "0900543370", "074"
  ],
  "Madison": [
    "Madison", "Madison, Connecticut", "Madison, CT", "Madison CT",
    "06443",
    "0900944560", "076"
  ],
  "Manchester": [
    "Manchester", "Manchester, Connecticut", "Manchester, CT", "Manchester CT",
    "06040", "06041", "06042", "06043", "06045",
    "0900344700", "077"
  ],
  "Mansfield": [
    "Mansfield", "Mansfield, Connecticut", "Mansfield, CT", "Mansfield CT",
    "06250", "06268",
    "0901344910", "078"
  ],
  "Mansfield Center": [
    "Mansfield Center", "Mansfield Center, Connecticut", "Mansfield Center, CT", "Mansfield Center CT",
    "06250"
  ],
  "Mansfield Depot": [
    "Mansfield Depot", "Mansfield Depot, Connecticut", "Mansfield Depot, CT", "Mansfield Depot CT",
    "06251"
  ],
  "Masons Island": [
    "Masons Island", "Masons Island, Connecticut", "Masons Island, CT", "Masons Island CT",
    "06355"
  ],
  "Melrose": [
    "Melrose", "Melrose, Connecticut", "Melrose, CT", "Melrose CT",
    "06049"
  ],
  "Meriden": [
    "Meriden", "Meriden, Connecticut", "Meriden, CT", "Meriden CT",
    "06450", "06451", "06454",
    "0900946520", "080"
  ],
  "Middle Haddam": [
    "Middle Haddam", "Middle Haddam, Connecticut", "Middle Haddam, CT", "Middle Haddam CT",
    "06456"
  ],
  "Middlebury": [
    "Middlebury", "Middlebury, Connecticut", "Middlebury, CT", "Middlebury CT",
    "06762",
    "0900946940", "081"
  ],
  "Middlefield": [
    "Middlefield", "Middlefield, Connecticut", "Middlefield, CT", "Middlefield CT",
    "06455",
    "0900747080", "082"
  ],
  "Middletown": [
    "Middletown", "Middletown, Connecticut", "Middletown, CT", "Middletown CT",
    "06457", "06459",
    "0900747360", "083"
  ],
  "Milford": [
    "Milford", "Milford, Connecticut", "Milford, CT", "Milford CT",
    "06460", "06461", "06466",
    "0900947535", "084"
  ],
  "Milldale": [
    "Milldale", "Milldale, Connecticut", "Milldale, CT", "Milldale CT",
    "06467"
  ],
  "Monroe": [
    "Monroe", "Monroe, Connecticut", "Monroe, CT", "Monroe CT",
    "06468",
    "0900148620", "085"
  ],
  "Moodus": [
    "Moodus", "Moodus, Connecticut", "Moodus, CT", "Moodus CT",
    "06469"
  ],
  "Montville": [
    "Montville", "Montville, Connecticut", "Montville, CT", "Montville CT",
    "06353",
    "0901148900", "086"
  ],
  "Morris": [
    "Morris", "Morris, Connecticut", "Morris, CT", "Morris CT",
    "06758", "06763",
    "0900549460", "087"
  ],
  "Mystic": [
    "Mystic", "Mystic, Connecticut", "Mystic, CT", "Mystic CT",
    "06355", "06388"
  ],
  "Nepaug": [
    "Nepaug", "Nepaug, Connecticut", "Nepaug, CT", "Nepaug CT",
    "06057"
  ],
  "New Britain": [
    "New Britain", "New Britain, Connecticut", "New Britain, CT", "New Britain CT",
    "06050", "06051", "06052", "06053",
    "0900350440", "089"
  ],
  "New Canaan": [
    "New Canaan", "New Canaan, Connecticut", "New Canaan, CT", "New Canaan CT",
    "06840", "06842",
    "0900150580", "090"
  ],
  "New Fairfield": [
    "New Fairfield", "New Fairfield, Connecticut", "New Fairfield, CT", "New Fairfield CT",
    "06812",
    "0900150860", "091"
  ],
  "New Hartford": [
    "New Hartford", "New Hartford, Connecticut", "New Hartford, CT", "New Hartford CT",
    "06057",
    "0900551350", "092"
  ],
  "New Haven": [
    "New Haven", "New Haven, Connecticut", "New Haven, CT", "New Haven CT",
    "06501", "06502", "06503", "06504", "06505", "06506", "06507", "06508", "06509", "06510",
    "06511", "06512", "06513", "06514", "06515", "06516", "06517", "06518", "06519", "06520",
    "06521", "06524", "06525", "06530", "06531", "06532", "06533", "06534", "06535", "06536",
    "06537", "06538", "06540",
    "0900952070", "093"
  ],
  "New London": [
    "New London", "New London, Connecticut", "New London, CT", "New London CT",
    "06320",
    "0901152350", "095"
  ],
  "New Milford": [
    "New Milford", "New Milford, Connecticut", "New Milford, CT", "New Milford CT",
    "06776",
    "0900552630", "096"
  ],
  "Newington": [
    "Newington", "Newington, Connecticut", "Newington, CT", "Newington CT",
    "06111", "06131",
    "0900352140", "094"
  ],
  "New Preston": [
    "New Preston", "New Preston, Connecticut", "New Preston, CT", "New Preston CT",
    "06777"
  ],
  "New Preston Marble Dale": [
    "New Preston Marble Dale", "New Preston Marble Dale, Connecticut", "New Preston Marble Dale, CT", "New Preston Marble Dale CT",
    "06777"
  ],
  "Newtown": [
    "Newtown", "Newtown, Connecticut", "Newtown, CT", "Newtown CT",
    "06470",
    "0900152980", "097"
  ],
  "Niantic": [
    "Niantic", "Niantic, Connecticut", "Niantic, CT", "Niantic CT",
    "06357"
  ],
  "Noank": [
    "Noank", "Noank, Connecticut", "Noank, CT", "Noank CT",
    "06340"
  ],
  "Norfolk": [
    "Norfolk", "Norfolk, Connecticut", "Norfolk, CT", "Norfolk CT",
    "06058",
    "0900553470", "098"
  ],
  "Noroton Heights": [
    "Noroton Heights", "Noroton Heights, Connecticut", "Noroton Heights, CT", "Noroton Heights CT",
    "06820"
  ],
  "North Branford": [
    "North Branford", "North Branford, Connecticut", "North Branford, CT", "North Branford CT",
    "06471",
    "0900953890", "099"
  ],
  "North Canaan": [
    "North Canaan", "North Canaan, Connecticut", "North Canaan, CT", "North Canaan CT",
    "06018",
    "0900554030", "100"
  ],
  "North Canton": [
    "North Canton", "North Canton, Connecticut", "North Canton, CT", "North Canton CT",
    "06059"
  ],
  "North Franklin": [
    "North Franklin", "North Franklin, Connecticut", "North Franklin, CT", "North Franklin CT",
    "06254"
  ],
  "North Granby": [
    "North Granby", "North Granby, Connecticut", "North Granby, CT", "North Granby CT",
    "06060"
  ],
  "North Grosvenordale": [
    "North Grosvenordale", "North Grosvenordale, Connecticut", "North Grosvenordale, CT", "North Grosvenordale CT",
    "06255"
  ],
  "North Haven": [
    "North Haven", "North Haven, Connecticut", "North Haven, CT", "North Haven CT",
    "06473",
    "0900954870", "101"
  ],
  "North Sterling": [
    "North Sterling", "North Sterling, Connecticut", "North Sterling, CT", "North Sterling CT",
    "06377"
  ],
  "North Stonington": [
    "North Stonington", "North Stonington, Connecticut", "North Stonington, CT", "North Stonington CT",
    "06359",
    "0901155500", "102"
  ],
  "North Westchester": [
    "North Westchester", "North Westchester, Connecticut", "North Westchester, CT", "North Westchester CT",
    "06474"
  ],
  "North Windham": [
    "North Windham", "North Windham, Connecticut", "North Windham, CT", "North Windham CT",
    "06256"
  ],
  "Norwalk": [
    "Norwalk", "Norwalk, Connecticut", "Norwalk, CT", "Norwalk CT",
    "06850", "06851", "06852", "06853", "06854", "06855", "06856", "06857", "06858", "06859", "06860",
    "0900156060", "103"
  ],
  "Norwich": [
    "Norwich", "Norwich, Connecticut", "Norwich, CT", "Norwich CT",
    "06360", "06365",
    "104"  # Tax code; FIPS listed as NA in your table rows for Norwich
  ],
  "Norwichtown": [
    "Norwichtown", "Norwichtown, Connecticut", "Norwichtown, CT", "Norwichtown CT",
    "06360"
  ],
  "Occum": [
    "Occum", "Occum, Connecticut", "Occum, CT", "Occum CT",
    "06360"
  ],
  "Oakdale": [
    "Oakdale", "Oakdale, Connecticut", "Oakdale, CT", "Oakdale CT",
    "06370"
  ],
  "Oakville": [
    "Oakville", "Oakville, Connecticut", "Oakville, CT", "Oakville CT",
    "06779"
  ],
  "Occum": [
    "Occum", "Occum, Connecticut", "Occum, CT", "Occum CT",
    "06360"
  ],
  "Old Greenwich": [
    "Old Greenwich", "Old Greenwich, Connecticut", "Old Greenwich, CT", "Old Greenwich CT",
    "06870"
  ],
  "Old Lyme": [
    "Old Lyme", "Old Lyme, Connecticut", "Old Lyme, CT", "Old Lyme CT",
    "06371",
    "0901157040", "105"
  ],
  "Old Mystic": [
    "Old Mystic", "Old Mystic, Connecticut", "Old Mystic, CT", "Old Mystic CT",
    "06372"
  ],
  "Old Saybrook": [
    "Old Saybrook", "Old Saybrook, Connecticut", "Old Saybrook, CT", "Old Saybrook CT",
    "06475",
    "0900757320", "106"
  ],
  "Orange": [
    "Orange", "Orange, Connecticut", "Orange, CT", "Orange CT",
    "06477",
    "0900957600", "107"
  ],
  "Oxford": [
    "Oxford", "Oxford, Connecticut", "Oxford, CT", "Oxford CT",
    "06478",
    "0900958300", "108"
  ],
  "Pawcatuck": [
    "Pawcatuck", "Pawcatuck, Connecticut", "Pawcatuck, CT", "Pawcatuck CT",
    "06379"
  ],
  "Pequabuck": [
    "Pequabuck", "Pequabuck, Connecticut", "Pequabuck, CT", "Pequabuck CT",
    "06781"
  ],
  "Pine Meadow": [
    "Pine Meadow", "Pine Meadow, Connecticut", "Pine Meadow, CT", "Pine Meadow CT",
    "06061"
  ],
  "Plainfield": [
    "Plainfield", "Plainfield, Connecticut", "Plainfield, CT", "Plainfield CT",
    "06374",
    "0901559980", "109"
  ],
  "Plainville": [
    "Plainville", "Plainville, Connecticut", "Plainville, CT", "Plainville CT",
    "06062",
    "0900360120", "110"
  ],
  "Plantsville": [
    "Plantsville", "Plantsville, Connecticut", "Plantsville, CT", "Plantsville CT",
    "06479"
  ],
  "Pleasant Valley": [
    "Pleasant Valley", "Pleasant Valley, Connecticut", "Pleasant Valley, CT", "Pleasant Valley CT",
    "06063"
  ],
  "Poquonock": [
    "Poquonock", "Poquonock, Connecticut", "Poquonock, CT", "Poquonock CT",
    "06064"
  ],
  "Poquetanuck": [
    "Poquetanuck", "Poquetanuck, Connecticut", "Poquetanuck, CT", "Poquetanuck CT",
    "06360"
  ],
  "Pomfret": [
    "Pomfret", "Pomfret, Connecticut", "Pomfret, CT", "Pomfret CT",
    "06258",
    "0901561030", "112"
  ],
  "Pomfret Center": [
    "Pomfret Center", "Pomfret Center, Connecticut", "Pomfret Center, CT", "Pomfret Center CT",
    "06259"
  ],
  "Portland": [
    "Portland", "Portland, Connecticut", "Portland, CT", "Portland CT",
    "06480",
    "0900761800", "113"
  ],
  "Preston": [
    "Preston", "Preston, Connecticut", "Preston, CT", "Preston CT",
    "06365",
    "0901162150", "114"
  ],
  "Prospect": [
    "Prospect", "Prospect, Connecticut", "Prospect, CT", "Prospect CT",
    "06712",
    "0900962290", "115"
  ],
  "Putnam": [
    "Putnam", "Putnam, Connecticut", "Putnam, CT", "Putnam CT",
    "06260",
    "0901562710", "116"
  ],
  "Quaker Hill": [
    "Quaker Hill", "Quaker Hill, Connecticut", "Quaker Hill, CT", "Quaker Hill CT",
    "06375"
  ],
  "Quinebaug": [
    "Quinebaug", "Quinebaug, Connecticut", "Quinebaug, CT", "Quinebaug CT",
    "06262"
  ],
  "Redding": [
    "Redding", "Redding, Connecticut", "Redding, CT", "Redding CT",
    "06875", "06896",
    "0900163480", "117"
  ],
  "Redding Center": [
    "Redding Center", "Redding Center, Connecticut", "Redding Center, CT", "Redding Center CT",
    "06875"
  ],
  "Redding Ridge": [
    "Redding Ridge", "Redding Ridge, Connecticut", "Redding Ridge, CT", "Redding Ridge CT",
    "06876"
  ],
  "Ridgefield": [
    "Ridgefield", "Ridgefield, Connecticut", "Ridgefield, CT", "Ridgefield CT",
    "06877", "06879",
    "0900163970", "118"
  ],
  "Riverside": [
    "Riverside", "Riverside, Connecticut", "Riverside, CT", "Riverside CT",
    "06878"
  ],
  "Riverton": [
    "Riverton", "Riverton, Connecticut", "Riverton, CT", "Riverton CT",
    "06065"
  ],
  "Rockfall": [
    "Rockfall", "Rockfall, Connecticut", "Rockfall, CT", "Rockfall CT",
    "06481"
  ],
  "Rockville": [
    "Rockville", "Rockville, Connecticut", "Rockville, CT", "Rockville CT",
    "06066"
  ],
  "Rocky Hill": [
    "Rocky Hill", "Rocky Hill, Connecticut", "Rocky Hill, CT", "Rocky Hill CT",
    "06067",
    "0900365370", "119"
  ],
  "Rogers": [
    "Rogers", "Rogers, Connecticut", "Rogers, CT", "Rogers CT",
    "06263"
  ],
  "Roxbury": [
    "Roxbury", "Roxbury, Connecticut", "Roxbury, CT", "Roxbury CT",
    "06783",
    "0900565930", "120"
  ],
  "Salisbury": [
    "Salisbury", "Salisbury, Connecticut", "Salisbury, CT", "Salisbury CT",
    "06068", "06079",
    "0900566420", "122"
  ],
  "Sandy Hook": [
    "Sandy Hook", "Sandy Hook, Connecticut", "Sandy Hook, CT", "Sandy Hook CT",
    "06482"
  ],
  "Scotland": [
    "Scotland", "Scotland, Connecticut", "Scotland, CT", "Scotland CT",
    "06264",
    "0901567400", "123"
  ],
  "Seymour": [
    "Seymour", "Seymour, Connecticut", "Seymour, CT", "Seymour CT",
    "06478", "06483",
    "0900967610", "124"
  ],
  "Sharon": [
    "Sharon", "Sharon, Connecticut", "Sharon, CT", "Sharon CT",
    "06069",
    "0900567960", "125"
  ],
  "Sherman": [
    "Sherman", "Sherman, Connecticut", "Sherman, CT", "Sherman CT",
    "06784",
    "0900168310", "127"
  ],
  "Simsbury": [
    "Simsbury", "Simsbury, Connecticut", "Simsbury, CT", "Simsbury CT",
    "06070", "06081", "06092",
    "0900368940", "128"
  ],
  "Somers": [
    "Somers", "Somers, Connecticut", "Somers, CT", "Somers CT",
    "06071", "06072",
    "0901369220", "129"
  ],
  "Somersville": [
    "Somersville", "Somersville, Connecticut", "Somersville, CT", "Somersville CT",
    "06072"
  ],
  "South Britain": [
    "South Britain", "South Britain, Connecticut", "South Britain, CT", "South Britain CT",
    "06487"
  ],
  "South Glastonbury": [
    "South Glastonbury", "South Glastonbury, Connecticut", "South Glastonbury, CT", "South Glastonbury CT",
    "06073"
  ],
  "South Kent": [
    "South Kent", "South Kent, Connecticut", "South Kent, CT", "South Kent CT",
    "06785"
  ],
  "South Lyme": [
    "South Lyme", "South Lyme, Connecticut", "South Lyme, CT", "South Lyme CT",
    "06376"
  ],
  "South Norwalk": [
    "South Norwalk", "South Norwalk, Connecticut", "South Norwalk, CT", "South Norwalk CT",
    "06854"
  ],
  "South Willington": [
    "South Willington", "South Willington, Connecticut", "South Willington, CT", "South Willington CT",
    "06265"
  ],
  "South Windham": [
    "South Windham", "South Windham, Connecticut", "South Windham, CT", "South Windham CT",
    "06266"
  ],
  "South Windsor": [
    "South Windsor", "South Windsor, Connecticut", "South Windsor, CT", "South Windsor CT",
    "06074",
    "0900371390", "132"
  ],
  "South Woodstock": [
    "South Woodstock", "South Woodstock, Connecticut", "South Woodstock, CT", "South Woodstock CT",
    "06267"
  ],
  "Southbury": [
    "Southbury", "Southbury, Connecticut", "Southbury, CT", "Southbury CT",
    "06488",
    "0900969640", "130"
  ],
  "Southport": [
    "Southport", "Southport, Connecticut", "Southport, CT", "Southport CT",
    "06490"
  ],
  "Southington": [
    "Southington", "Southington, Connecticut", "Southington, CT", "Southington CT",
    "06489",
    "0900370550", "131"
  ],
  "Sprague": [
    "Sprague", "Sprague, Connecticut", "Sprague, CT", "Sprague CT",
    "06330",
    "0901171670", "133"
  ],
  "Stamford": [
    "Stamford", "Stamford, Connecticut", "Stamford, CT", "Stamford CT",
    "06901", "06902", "06903", "06904", "06905", "06906", "06907", "06910", "06911", "06912",
    "06913", "06914", "06920", "06921", "06922", "06925", "06926", "06927", "06928",
    "0900173070", "135"
  ],
  "Sterling": [
    "Sterling", "Sterling, Connecticut", "Sterling, CT", "Sterling CT",
    "06377",
    "0901573420", "136"
  ],
  "Stevenson": [
    "Stevenson", "Stevenson, Connecticut", "Stevenson, CT", "Stevenson CT",
    "06491"
  ],
  "Stepney": [
    "Stepney", "Stepney, Connecticut", "Stepney, CT", "Stepney CT",
    "06468"
  ],
  "Stonington": [
    "Stonington", "Stonington, Connecticut", "Stonington, CT", "Stonington CT",
    "06378",
    "0901173770", "137"
  ],
  "Storrs": [
    "Storrs", "Storrs, Connecticut", "Storrs, CT", "Storrs CT",
    "06268"
  ],
  "Storrs Mansfield": [
    "Storrs Mansfield", "Storrs Mansfield, Connecticut", "Storrs Mansfield, CT", "Storrs Mansfield CT",
    "06268", "06269"
  ],
  "Stratford": [
    "Stratford", "Stratford, Connecticut", "Stratford, CT", "Stratford CT",
    "06497", "06614", "06615",
    "0900174190", "138"
  ],
  "Suffield": [
    "Suffield", "Suffield, Connecticut", "Suffield, CT", "Suffield CT",
    "06078", "06080",
    "0900374540", "139"
  ],
  "Taconic": [
    "Taconic", "Taconic, Connecticut", "Taconic, CT", "Taconic CT",
    "06079"
  ],
  "Talcottville": [
    "Talcottville", "Talcottville, Connecticut", "Talcottville, CT", "Talcottville CT",
    "06066"
  ],
  "Taftville": [
    "Taftville", "Taftville, Connecticut", "Taftville, CT", "Taftville CT",
    "06380"
  ],
  "Tariffville": [
    "Tariffville", "Tariffville, Connecticut", "Tariffville, CT", "Tariffville CT",
    "06081"
  ],
  "Terryville": [
    "Terryville", "Terryville, Connecticut", "Terryville, CT", "Terryville CT",
    "06786"
  ],
  "Thomaston": [
    "Thomaston", "Thomaston, Connecticut", "Thomaston, CT", "Thomaston CT",
    "06778", "06787",
    "0900575730", "140"
  ],
  "Thompson": [
    "Thompson", "Thompson, Connecticut", "Thompson, CT", "Thompson CT",
    "06277",
    "0901575870", "141"
  ],
  "Tolland": [
    "Tolland", "Tolland, Connecticut", "Tolland, CT", "Tolland CT",
    "06084",
    "0901376290", "142"
  ],
  "Torrington": [
    "Torrington", "Torrington, Connecticut", "Torrington, CT", "Torrington CT",
    "06790", "06791",
    "0900576570", "143"
  ],
  "Turnpike": [
    "Turnpike", "Turnpike, Connecticut", "Turnpike, CT", "Turnpike CT",
    "06066"
  ],
  "Uncasville": [
    "Uncasville", "Uncasville, Connecticut", "Uncasville, CT", "Uncasville CT",
    "06382"
  ],
  "Union": [
    "Union", "Union, Connecticut", "Union, CT", "Union CT",
    "06076",
    "0901377830", "145"
  ],
  "Unionville": [
    "Unionville", "Unionville, Connecticut", "Unionville, CT", "Unionville CT",
    "06013", "06085", "06087"
  ],
  "Vernon": [
    "Vernon", "Vernon, Connecticut", "Vernon, CT", "Vernon CT",
    "06066",
    "0901378250", "146"
  ],
  "Vernon Rockville": [
    "Vernon Rockville", "Vernon Rockville, Connecticut", "Vernon Rockville, CT", "Vernon Rockville CT",
    "06066"
  ],
  "Versailles": [
    "Versailles", "Versailles, Connecticut", "Versailles, CT", "Versailles CT",
    "06383"
  ],
  "Voluntown": [
    "Voluntown", "Voluntown, Connecticut", "Voluntown, CT", "Voluntown CT",
    "06384",
    "0901178600", "147"
  ],
  "Wallingford": [
    "Wallingford", "Wallingford, Connecticut", "Wallingford, CT", "Wallingford CT",
    "06492", "06493", "06494", "06495",
    "0900978740", "148"
  ],
  "Wapping": [
    "Wapping", "Wapping, Connecticut", "Wapping, CT", "Wapping CT",
    "06074"
  ],
  "Warrenville": [
    "Warrenville", "Warrenville, Connecticut", "Warrenville, CT", "Warrenville CT",
    "06278"
  ],
  "Warren": [
    "Warren", "Warren, Connecticut", "Warren, CT", "Warren CT",
    "06754",
    "0900579510", "149"
  ],
  "Washington": [
    "Washington", "Washington, Connecticut", "Washington, CT", "Washington CT",
    "06777", "06793", "06794",
    "0900579720", "150"
  ],
  "Washington Depot": [
    "Washington Depot", "Washington Depot, Connecticut", "Washington Depot, CT", "Washington Depot CT",
    "06777", "06793", "06794"
  ],
  "Waterbury": [
    "Waterbury", "Waterbury, Connecticut", "Waterbury, CT", "Waterbury CT",
    "06701", "06702", "06703", "06704", "06705", "06706", "06708", "06710", "06712", "06716",
    "06720", "06721", "06722", "06723", "06724", "06725", "06726", "06749",
    "0900980070", "151"
  ],
  "Waterford": [
    "Waterford", "Waterford, Connecticut", "Waterford, CT", "Waterford CT",
    "06385", "06386",
    "0901180280", "152"
  ],
  "Watertown": [
    "Watertown", "Watertown, Connecticut", "Watertown, CT", "Watertown CT",
    "06779", "06795",
    "0900580490", "153"
  ],
  "Wauregan": [
    "Wauregan", "Wauregan, Connecticut", "Wauregan, CT", "Wauregan CT",
    "06387"
  ],
  "Warehouse Point": [
    "Warehouse Point", "Warehouse Point, Connecticut", "Warehouse Point, CT", "Warehouse Point CT",
    "06088"
  ],
  "Weatogue": [
    "Weatogue", "Weatogue, Connecticut", "Weatogue, CT", "Weatogue CT",
    "06089"
  ],
  "West Cornwall": [
    "West Cornwall", "West Cornwall, Connecticut", "West Cornwall, CT", "West Cornwall CT",
    "06796"
  ],
  "West Granby": [
    "West Granby", "West Granby, Connecticut", "West Granby, CT", "West Granby CT",
    "06090"
  ],
  "West Hartford": [
    "West Hartford", "West Hartford, Connecticut", "West Hartford, CT", "West Hartford CT",
    "06107", "06110", "06117", "06119", "06127", "06133", "06137",
    "0900382590", "155"
  ],
  "West Hartland": [
    "West Hartland", "West Hartland, Connecticut", "West Hartland, CT", "West Hartland CT",
    "06091"
  ],
  "West Haven": [
    "West Haven", "West Haven, Connecticut", "West Haven, CT", "West Haven CT",
    "06516",
    "0900982870", "156"
  ],
  "West Simsbury": [
    "West Simsbury", "West Simsbury, Connecticut", "West Simsbury, CT", "West Simsbury CT",
    "06092"
  ],
  "West Stafford": [
    "West Stafford", "West Stafford, Connecticut", "West Stafford, CT", "West Stafford CT",
    "06076"
  ],
  "West Suffield": [
    "West Suffield", "West Suffield, Connecticut", "West Suffield, CT", "West Suffield CT",
    "06093"
  ],
  "Westbrook": [
    "Westbrook", "Westbrook, Connecticut", "Westbrook, CT", "Westbrook CT",
    "06498",
    "0900781680", "154"
  ],
  "Weston": [
    "Weston", "Weston, Connecticut", "Weston, CT", "Weston CT",
    "06883",
    "0900183430", "157"
  ],
  "Westport": [
    "Westport", "Westport, Connecticut", "Westport, CT", "Westport CT",
    "06880", "06881", "06888", "06889",
    "0900183500", "158"
  ],
  "Wethersfield": [
    "Wethersfield", "Wethersfield, Connecticut", "Wethersfield, CT", "Wethersfield CT",
    "06109", "06129",
    "0900384900", "159"
  ],
  "Willimantic": [
    "Willimantic", "Willimantic, Connecticut", "Willimantic, CT", "Willimantic CT",
    "06226"
  ],
  "Willington": [
    "Willington", "Willington, Connecticut", "Willington, CT", "Willington CT",
    "06279",
    "0901385950", "160"
  ],
  "Windham": [
    "Windham", "Windham, Connecticut", "Windham, CT", "Windham CT",
    "06256", "06280",
    "0901586790", "163"
  ],
  "Windsor": [
    "Windsor", "Windsor, Connecticut", "Windsor, CT", "Windsor CT",
    "06006", "06064", "06095",
    "0900387000", "164"
  ],
  "Windsor Locks": [
    "Windsor Locks", "Windsor Locks, Connecticut", "Windsor Locks, CT", "Windsor Locks CT",
    "06096",
    "0900387070", "165"
  ],
  "Winchester": [
    "Winchester", "Winchester, Connecticut", "Winchester, CT", "Winchester CT",
    "06094", "06098",
    "0900586440", "162"
  ],
  "Winchester Center": [
    "Winchester Center", "Winchester Center, Connecticut", "Winchester Center, CT", "Winchester Center CT",
    "06094"
  ],
  "Winsted": [
    "Winsted", "Winsted, Connecticut", "Winsted, CT", "Winsted CT",
    "06094", "06098"
  ],
  "Wolcott": [
    "Wolcott", "Wolcott, Connecticut", "Wolcott, CT", "Wolcott CT",
    "06716",
    "0900987560", "166"
  ],
  "Woodbridge": [
    "Woodbridge", "Woodbridge, Connecticut", "Woodbridge, CT", "Woodbridge CT",
    "06525",
    "0900987700", "167"
  ],
  "Woodbury": [
    "Woodbury", "Woodbury, Connecticut", "Woodbury, CT", "Woodbury CT",
    "06798",
    "0900587910", "168"
  ],
  "Woodstock": [
    "Woodstock", "Woodstock, Connecticut", "Woodstock, CT", "Woodstock CT",
    "06281",
    "0901588190", "169"
  ],
  "Woodstock Valley": [
    "Woodstock Valley", "Woodstock Valley, Connecticut", "Woodstock Valley, CT", "Woodstock Valley CT",
    "06282"
  ],
  "Yalesville": [
    "Yalesville", "Yalesville, Connecticut", "Yalesville, CT", "Yalesville CT",
    "06492"
  ],
  "Yantic": [
    "Yantic", "Yantic, Connecticut", "Yantic, CT", "Yantic CT",
    "06389"
  ]
}

GENDER_MAPPING = {
    "Male": [
        "Male", "Man", "M", "Trans Male", "Transgender man",
        "Hombre", "Masculino", "Homem",  # ES, PT
        "Homme", "Hommes",               # FR
        "1"  # WIOA Sex code for Male
    ],
    "Female": [
        "Female", "Woman", "F", "Trans Female", "Transgender woman",
        "Mujer", "Feminino", "Femme",     # ES, PT, FR
        "2"  # WIOA Sex code for Female
    ],
    "Other": [
        "Transgender", "Non-Binary", "Nonbinary", "Genderqueer",
        "Prefer to self-identify"
    ],
    "Unknown": [
        "Prefer not to answer", "Did not disclose", "Choose not to answer",
        "", None, "9"  # WIOA non-disclosure
    ]
}

DISABILITY_MAPPING = {
    '1': ['Yes', '1', '2', '3', '4', '5', '6', 'True', 'true', 'Y', 'y', 'Sí', 'Sim', 'Oui'],  # ES, PT, FR, 1-6 for PIRL 203 listing diff types of disabilities
    '0': ['No', '0', 'False', 'false', 'N', 'n', 'No', 'Não', 'Non'],  # ES, PT, FR
    'Unknown': ['Prefer not to answer', 'Did not disclose', 'Choose not to answer', '', None, '9']  # 9 is WIOA non-disclosure  
}

EMPLOYMENT_STATUS_MAPPING = {
    'Employed; Full-time': ['Employed; Full-time', 'full-time', 'Completed-Employed', '1' 
                            # 'self-employed',  # Uncomment these rows if we want to combine these options as only employed; full-time. Thinking best to keep it granular here then group more in PBI and later
                            # 'Employed in-field by an employer who partners with your training program',
                            # 'Employed in-field by an employer who doesn\'t partner with your training program',
                            # 'Employed out of field',
                            ], # Leave the \'t in doesn't b/c this shows the computer the 't in "doesn't" is part of the string and not a string delimiter
    'self-employed': ['self-employed'], # self-employed is a WIOA code for Employed at Exit
    'Employed in-field by an employer who partners with your training program': ['Employed in-field by an employer who partners with your training program'],
    'Employed in-field by an employer who doesn\'t partner with your training program': ['Employed in-field by an employer who doesn\'t partner with your training program'],
    'Employed out of field': ['Employed out of field'], 
    'Employed; Part-time': ['Employed; Part-time', 'part-time'],
    'Temporarily employed': ['Temporarily employed'],
    'Internship': ['Internship', 'paid internship/work experience'],
    'Apprenticeship': ['Apprenticeship'], 
    'Further Education': ['Completed-Enrolled in PSEd or Adv Trng or Mil'], # WIOA code for Employed at Exit
    'Unemployed': ['Not Employed', 'Unemployed','Completed-Unemployed', '2', 
                   'Still seeking employment', 'Not seeking employment in-field'],
    'Unknown': ['Unknown', 'Prefer not to answer', 'Did not disclose', 'Choose not to answer', 'Could not contact','', None, '9']  # WIOA non-disclosure
  }  

ETHNICITY_MAPPING = {
    "Hispanic": [
        "Hispanic", "Latino", "or Spanish", "Hispanic, Latino, or Spanish",
        "Hispano", "latino o español", "Hispano, latino o español",
        "Hispânicos", "latinos ou espanhóis", "Hispânicos, latinos ou espanhóis",
        "Hispanique", "latino ou espagnol", "Hispanique, latino ou espangnol",
        "1", "Hispanic or Latino"  # WIOA code
    ],
    "non-Hispanic": [
        "Not Hispanic", "non-Hispanic", "Non-Hispanic",
        "Not Hispanic or Latino", "Non-Hispanic or Latino",
        "0"  # WIOA code
    ],
    "Unknown": [
        "Prefer not to answer", "DID NOT DISCLOSE", "Choose not to answer",
        "", None, "9"  # WIOA unknown
    ]
}

RACE_MAPPING = {
    "Black": [
        "Black", "Black or African American", "Black / African American",
        "Noirs ou afro-américains", "Negro o afroamericano",
        "Negro ou afro-americano", "213"
    ],
    "White": ["White", "Caucasian or White", "Blanc", "215"],
    "Asian": ["Asian", "212"],
    "American Indian": ["American Indian or Alaska Native", "211"],
    "Hawaiian/Pacific Islander": ["Native Hawaiian or Other Pacific Islander", "214"],
    "Multi-Racial": ["Multi-racial"],
    "Other": ["Other", "Prefer to self-identify"],
    "Unknown": ["Prefer not to answer", "DID NOT DISCLOSE", "Choose not to answer", "", None]
}

DISLOCATED_WORKER_MAPPING = {
    "terminated_or_laid_off": ['1'],
    "received_services_WIOA_133a": ['2'],
    "received_services_WIOA133b2B_and_133a": ['3'],
    "intent_to_use_services_and_eligible": ['4'],
    "did_not_receive_services": ['0']
}

INCUMBENT_WORKER_MAPPING = {
    "TBD": ['tbd']
}

RACE_ETHNICITY_MAPPING = {
     "Black": [
        "Black", "Black or African American", "Black / African American",
        "Noirs ou afro-américains", "Negro o afroamericano",
        "Negro ou afro-americano", "213"
    ],
    "White": ["White", "Caucasian or White", "Blanc", "215"],
    "Asian": ["Asian", "212"],
    "American Indian": ["American Indian or Alaska Native", "211"],
    "Hawaiian/Pacific Islander": ["Native Hawaiian or Other Pacific Islander", "214"],
    "Multi-Racial": ["Multi-racial"],
    "Other": ["Other", "Prefer to self-identify"],
    "Unknown": ["Prefer not to answer", "DID NOT DISCLOSE", "Choose not to answer", "", None],
    "Hispanic": [
        "Hispanic", "Latino", "or Spanish", "Hispanic, Latino, or Spanish",
        "Hispano", "latino o español", "Hispano, latino o español",
        "Hispânicos", "latinos ou espanhóis", "Hispânicos, latinos ou espanhóis",
        "Hispanique", "latino ou espagnol", "Hispanique, latino ou espangnol",
        "1", "Hispanic or Latino"  # WIOA code
    ],
    "non-Hispanic": [
        "Not Hispanic", "non-Hispanic", "Non-Hispanic",
        "Not Hispanic or Latino", "Non-Hispanic or Latino",
        "0"  # WIOA code
    ],
    "Unknown": [
        "Prefer not to answer", "DID NOT DISCLOSE", "Choose not to answer",
        "", None, "9"  # WIOA unknown
    ]
}

UC_MAPPING = {
    "TBD": ['tbd']
}


WAGNER_PEYSER_MAPPING = {
    "TBD": ['tbd']
}


YOUTH_PLACEMENT_MAPPING = {
    "TBD": ['tbd']
}

YOUTH_SERVICES_MAPPING = {
    "TBD": ['tbd']
}





# 1) Labels: { user_friendly_name: [unique Data Element values] }
simple_format_pa25_119_data_labels = {
    '1001 Date of First Basic Career Service (Staff-Assisted)': [
        '1001 Date of First Basic Career Service (Staff-Assisted)',
    ],
    '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)': [
        '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)',
    ],
    '1004 Date of Most Recent Career Service (WIOA)': [
        '1004 Date of Most Recent Career Service (WIOA)',
    ],
    '1007 Date of Most Recent Reportable Individual Contact': [
        '1007 Date of Most Recent Reportable Individual Contact',
    ],
    '105 Special Project ID - 1': [
        '105 Special Project ID - 1',
    ],
    '106 Special Project ID - 2': [
        '106 Special Project ID - 2',
    ],
    '107 Special Project ID - 3': [
        '107 Special Project ID - 3',
    ],
    '1200 Date of First Individualized Career Service': [
        '1200 Date of First Individualized Career Service',
    ],
    '1201 Most Recent Date Received Individualized Career Service': [
        '1201 Most Recent Date Received Individualized Career Service',
    ],
    '1205 Type of Work Experience': [
        '1205 Type of Work Experience',
    ],
    '12_month_date_benchmark': [
        '12 Month Date - benchmark',
    ],
    '12_months_employed': [
        '12 Months Continuously Employed',
    ],
    '1328 Training Provided Virtual/Online': [
        '1328 Training Provided Virtual/Online',
    ],
    '1331 Training Leading to an Associate Degree': [
        '1331 Training Leading to an Associate Degree',
    ],
    '1332 Participated in Postsecondary Education During Program Participation': [
        '1332 Participated in Postsecondary Education During Program Participation',
    ],
    '1332 Participated in Postsecondary Education During Program Participation (WIOA)': [
        '1332 Participated in Postsecondary Education During Program Participation (WIOA)',
    ],
    '1333 Received Private Sector Training': [
        '1333 Received Private Sector Training',
    ],
    '1333 Received training from program(s) operated by the private sector': [
        '1333 Received training from program(s) operated by the private sector',
    ],
    '1401 Enrolled in Secondary Education Program (WIOA)': [
        '1401 Enrolled in Secondary Education Program (WIOA)',
    ],
    '18_month_date_benchmark': [
        '18 Month Date - benchmark',
    ],
    '18_months_employed': [
        '18 Months Continuously Employed',
    ],
    '24_month_date_benchmark': [
        '24 Month Date - benchmark',
    ],
    '24_months_employed': [
        '24 Months Continuously Employed',
    ],
    '6_month_date_benchmark': [
        '6 Month Date - benchmark',
    ],
    '6_months_employed': [
        '6 Months Continuously Employed',
    ],
    '807 Displaced Homemaker at Program Entry (WIOA)': [
        '807 Displaced Homemaker at Program Entry (WIOA)',
    ],
    'Apt. Floor': [
        'Apt. Floor',
    ],
    'CATDLP': [
        'CATDLP',
    ],
    'CATP': [
        'CATP',
    ],
    'CDS eligibility': [
        'CDS eligibility',
    ],
    'CNA Certified Nursing Assistant - currently hold': [
        'CNA Certified Nursing Assistant - currently hold',
    ],
    'CTHires State ID': [
        'CTHires State ID',
    ],
    'Certification appointment date': [
        'Certification appointment date',
    ],
    'Certification appointment location': [
        'Certification appointment location',
    ],
    'Citizenship': [
        'Citizenship',
    ],
    'Closure Date': [
        'Closure Date',
    ],
    'Co-Enrolled': [
        'Co-Enrolled',
    ],
    'Co-funded': [
        'Co-funded',
    ],
    'Communication': [
        'Communication',
    ],
    'Completed80PercProg': [
        'Completed80PercProg',
    ],
    'Contact Location or Method': [
        'Contact Location or Method',
    ],
    'Contextualized Education': [
        'Contextualized Education',
    ],
    'Core Services to Employers': [
        'Core Services to Employers',
    ],
    'Cover Letter': [
        'Cover Letter',
    ],
    'Cover Letter Completed': [
        'Cover Letter Completed',
    ],
    'Critical Thinking/Problem Solving': [
        'Critical Thinking/Problem Solving',
    ],
    'Culinary Work Experience': [
        'Culinary Work Experience',
    ],
    'Currently Enrolled in WIOA': [
        'Currently Enrolled in WIOA',
    ],
    'Customer Service': [
        'Customer Service',
    ],
    'Dancing': [
        'Dancing',
    ],
    'Data Entry/Typing WPM': [
        'Data Entry/Typing WPM',
    ],
    'Date Co-Enrolled': [
        'Date Co-Enrolled',
    ],
    'Date Referral Made': [
        'Date Referral Made',
    ],
    'Date Status Updated': [
        'Date Status Updated',
    ],
    'Date Taken': [
        'Date Taken',
    ],
    'Deobligation Amount': [
        'Deobligation Amount',
    ],
    'Developed By': [
        'Developed By',
    ],
    'Did this individual enter new employment?': [
        'Did this individual enter new employment?',
    ],
    'Did youth attend Job Readiness Training?': [
        'Did youth attend Job Readiness Training?',
    ],
    'Diversity and Inclusion': [
        'Diversity and Inclusion',
    ],
    'Do you currently receive, or have you received in the past six months, any of the following?': [
        'Do you currently receive, or have you received in the past six months, any of the following?',
    ],
    'Do you have an LLC?': [
        'Do you have an LLC?',
    ],
    'Do you have an updated resume?': [
        'Do you have an updated resume?',
    ],
    'Do you have medical insurance?': [
        'Do you have medical insurance?',
    ],
    'Do you have stable housing?': [
        'Do you have stable housing?',
    ],
    'Do you have your high school credential (diploma or GED)?': [
        'Do you have your high school credential (diploma or GED)?',
    ],
    'Do you own a vehicle?': [
        'Do you own a vehicle?',
    ],
    'Do you speak a language, other than English, If so what?': [
        'Do you speak a language, other than English, If so what?',
    ],
    'Drywall Work Experience': [
        'Drywall Work Experience',
    ],
    'EB': [
        'EB',
    ],
    'EB_Job Title': [
        'EB_Job Title',
    ],
    'EB_JobOfferSTatus': [
        'EB_JobOfferSTatus',
    ],
    'EB_Start_Date': [
        'EB_Start_Date',
    ],
    'EB_Step': [
        'EB_Step',
    ],
    'EB_Wage': [
        'EB_Wage',
    ],
    'Electrical Work Experience': [
        'Electrical Work Experience',
    ],
    'Email': [
        'Email',
    ],
    'Employment Management (Job Seeking)': [
        'Employment Management (Job Seeking)',
    ],
    'Employment Readiness': [
        'Employment Readiness',
    ],
    'Engagement and Employer Onboarding': [
        'Engagement and Employer Onboarding',
    ],
    'Enrolled': [
        'Enrolled',
    ],
    'Entity Subtype': [
        'Entity Subtype',
    ],
    'Entity Type': [
        'Entity Type',
    ],
    'Entity Unique Identifier': [
        'Entity Unique Identifier',
    ],
    'Estimated Days in Training': [
        'Estimated Days in Training',
    ],
    'Estimated Number of Slots': [
        'Estimated Number of Slots',
    ],
    'Final Placement Status': [
        'Final Placement Status',
    ],
    'First Referral Date': [
        'First Referral Date',
    ],
    'General Construction Labor Work Experience': [
        'General Construction Labor Work Experience',
    ],
    'General Professionalism': [
        'General Professionalism',
    ],
    'HVAC Work Experience': [
        'HVAC Work Experience',
    ],
    'Have you attended any college or post-high school training?': [
        'Have you attended any college or post-high school training?',
    ],
    'Have you ever been incarcerated?': [
        'Have you ever been incarcerated?',
    ],
    'Have you ever owned a business?': [
        'Have you ever owned a business?',
    ],
    'Have you ever worked on a construction site?': [
        'Have you ever worked on a construction site?',
    ],
    'Have you participated in Summer Youth Program before?': [
        'Have you participated in Summer Youth Program before?',
    ],
    'Head of Household': [
        'Head of Household',
    ],
    'High School Diploma / GED': [
        'High School Diploma / GED',
    ],
    'Hire Count': [
        'Hire Count',
    ],
    'Hire Date': [
        'Hire Date',
    ],
    'Hired Permanently?': [
        'Hired Permanently?',
    ],
    'Hired by Worksite': [
        'Hired by Worksite',
    ],
    'How did you hear about this program?': [
        'How did you hear about this program?',
    ],
    'How many college credits have you earned?': [
        'How many college credits have you earned?',
    ],
    'How proficient are you with this language?': [
        'How proficient are you with this language?',
    ],
    'Identifier': [
        'Identifier',
    ],
    'If Other, please specify:': [
        'If Other, please specify:',
    ],
    'If earn and learn, type': [
        'If earn and learn, type',
    ],
    'If employed, did participant report hourly salary?': [
        'If employed, did participant report hourly salary?',
    ],
    'If other, describe': [
        'If other, describe',
    ],
    'If yes, how many years did you complete?': [
        'If yes, how many years did you complete?',
    ],
    'If yes, where and what did you do?': [
        'If yes, where and what did you do?',
    ],
    'If yes, where?': [
        'If yes, where?',
    ],
    'If you are attending college, Will you be going to college in fall?': [
        'If you are attending college, Will you be going to college in fall?',
    ],
    'IfNo-TerminationReason': [
        'IfNo-TerminationReason',
    ],
    'In the last 5 years, have you had an OSHA license?': [
        'In the last 5 years, have you had an OSHA license?',
    ],
    'Installation or Insulation Work Experience': [
        'Installation or Insulation Work Experience',
    ],
    'Intake Statuses': [
        'Intake Statuses',
    ],
    'Interested in: Computer Literacy': [
        'Interested in: Computer Literacy',
    ],
    'Interested in: Interview Preparation': [
        'Interested in: Interview Preparation',
    ],
    'Interested in: Resume Support': [
        'Interested in: Resume Support',
    ],
    'Interested in: Training': [
        'Interested in: Training',
    ],
    'Internet Search': [
        'Internet Search',
    ],
    'Interpersonal/Collaboration and Teamwork': [
        'Interpersonal/Collaboration and Teamwork',
    ],
    'Interview Date': [
        'Interview Date',
    ],
    'Is the vehicle registered and insured?': [
        'Is the vehicle registered and insured?',
    ],
    'Is this active military service?': [
        'Is this active military service?',
    ],
    'Is this job related to training received?': [
        'Is this job related to training received?',
    ],
    'JD End': [
        'JD End',
    ],
    'JD Exit Reason': [
        'JD Exit Reason',
    ],
    'JD Start': [
        'JD Start',
    ],
    'Job Application': [
        'Job Application',
    ],
    'Job Description': [
        'Job Description',
    ],
    'Job Developer': [
        'Job Developer',
    ],
    'Job Market': [
        'Job Market',
    ],
    'Job Referral': [
        'Job Referral',
    ],
    'Job Search': [
        'Job Search',
    ],
    'Jobs Funnel eligibility': [
        'Jobs Funnel eligibility',
    ],
    'LPN Licensed Practical Nurse - currently hold': [
        'LPN Licensed Practical Nurse - currently hold',
    ],
    'Labor Market and Employment Information Services are split across three areas.': [
        'Labor Market and Employment Information Services are split across three areas.',
    ],
    'Landscaping Work Experience': [
        'Landscaping Work Experience',
    ],
    'Last Modified': [
        'Last Modified',
    ],
    'Length of Agreement (Days)': [
        'Length of Agreement (Days)',
    ],
    'Low_AJC': [
        'Low_AJC',
    ],
    'MA Medical Assistant': [
        'MA Medical Assistant',
    ],
    'MPI Youth': [
        'MPI Youth',
    ],
    'Managing Region': [
        'Managing Region',
    ],
    'Manufacturing Machinist or CNC Work Experience': [
        'Manufacturing Machinist or CNC Work Experience',
    ],
    'Masonry Work Experience': [
        'Masonry Work Experience',
    ],
    'Medium_Remediation': [
        'Medium_Remediation',
    ],
    'Member of Populations': [
        'Member of Populations',
    ],
    'Microsoft Word, PowerPoint, Excel': [
        'Microsoft Word, PowerPoint, Excel',
    ],
    'Mock Interview': [
        'Mock Interview',
    ],
    'NAACP eligibility': [
        'NAACP eligibility',
    ],
    'New Skills Acquired (select all that apply)': [
        'New Skills Acquired (select all that apply)',
    ],
    'No Longer Available': [
        'No Longer Available',
    ],
    'Number of Slots Filled': [
        'Number of Slots Filled',
    ],
    'Office Equipment (i.e. copier, fax machine, scanner, etc.)': [
        'Office Equipment (i.e. copier, fax machine, scanner, etc.)',
    ],
    'Other': [
        'Other',
    ],
    'Other Costs': [
        'Other Costs',
    ],
    'Other Program Recommendation': [
        'Other Program Recommendation',
    ],
    'Other Skills (NAICS code)': [
        'Other Skills (NAICS code)',
    ],
    'PY15': [
        'PY15',
    ],
    'PY16': [
        'PY16',
    ],
    'PY17': [
        'PY17',
    ],
    'PY18': [
        'PY18',
    ],
    'PY19': [
        'PY19',
    ],
    'PY20': [
        'PY20',
    ],
    'PY21': [
        'PY21',
    ],
    'PY22': [
        'PY22',
    ],
    'PY23': [
        'PY23',
    ],
    'PY24': [
        'PY24',
    ],
    'PY25': [
        'PY25',
    ],
    'Painting Work Experience': [
        'Painting Work Experience',
    ],
    'Parent or Corporate Entity': [
        'Parent or Corporate Entity',
    ],
    'Participant Site Identifier': [
        'Participant Site Identifier',
    ],
    'Participant Status': [
        'Participant Status',
    ],
    'Partnership Activities': [
        'Partnership Activities',
    ],
    'Payroll Type': [
        'Payroll Type',
    ],
    'Pell Grant': [
        'Pell Grant',
    ],
    'Permanently Closed': [
        'Permanently Closed',
    ],
    'Phone Number': [
        'Phone Number',
    ],
    'Placed at Worksite?': [
        'Placed at Worksite?',
    ],
    'Plays an instrument': [
        'Plays an instrument',
    ],
    'Plumbing Work Experience': [
        'Plumbing Work Experience',
    ],
    'Position': [
        'Position',
    ],
    'Post-Secondary Plans': [
        'Post-Secondary Plans',
    ],
    'Prefix': [
        'Prefix',
    ],
    'Professionalism': [
        'Professionalism',
    ],
    'Program Vendor': [
        'Program Vendor',
    ],
    'Projected Completion Date': [
        'Projected Completion Date',
    ],
    'Pronouns': [
        'Pronouns',
    ],
    'Prove IT': [
        'Prove IT',
    ],
    'Quadrant of Residency': [
        'Quadrant of Residency',
    ],
    'RN Registered Nurse - currently hold': [
        'RN Registered Nurse - currently hold',
    ],
    'Reason for Referral': [
        'Reason for Referral',
    ],
    'Reason for Unfilled Slots': [
        'Reason for Unfilled Slots',
    ],
    'Reference Letters Completed': [
        'Reference Letters Completed',
    ],
    'Referral Closed': [
        'Referral Closed',
    ],
    'Referral Count': [
        'Referral Count',
    ],
    'Referral Status': [
        'Referral Status',
    ],
    'Referral to Workshop or Service': [
        'Referral to Workshop or Service',
    ],
    'Referred To': [
        'Referred To',
    ],
    'Registration Season(s)': [
        'Registration Season(s)',
    ],
    'Registration Year': [
        'Registration Year',
    ],
    'Registration Year:': [
        'Registration Year:',
    ],
    'Reporting Complete': [
        'Reporting Complete',
    ],
    'Resume Completed': [
        'Resume Completed',
    ],
    'Resume Creation': [
        'Resume Creation',
    ],
    'Resume Critique': [
        'Resume Critique',
    ],
    'Resume Revision': [
        'Resume Revision',
    ],
    'Secondary Education': [
        'Secondary Education',
    ],
    'SiMentor': [
        'SiMentor',
    ],
    'Special Requirements (check all that apply)': [
        'Special Requirements (check all that apply)',
    ],
    'Specify Other Post-Secondary Plans': [
        'Specify Other Post-Secondary Plans',
    ],
    'Specify Workshop or Service': [
        'Specify Workshop or Service',
    ],
    'Spoken Word or Poetry': [
        'Spoken Word or Poetry',
    ],
    'Status': [
        'Status',
    ],
    'Status Change': [
        'Status Change',
    ],
    'Status Change Date': [
        'Status Change Date',
    ],
    'Street Address': [
        'Street Address',
    ],
    'Student Key': [
        'Student Key',
    ],
    'Subsidized Loans': [
        'Subsidized Loans',
    ],
    'Summer Duties': [
        'Summer Duties',
    ],
    'Summer Worksite': [
        'Summer Worksite',
    ],
    'Swimming': [
        'Swimming',
    ],
    'Technology/Digital Literacy': [
        'Technology/Digital Literacy',
    ],
    'Test Score': [
        'Test Score',
    ],
    'Tests and Fees': [
        'Tests and Fees',
    ],
    'Tier': [
        'Tier',
    ],
    'Time/Self-Management': [
        'Time/Self-Management',
    ],
    'Total Number Provided': [
        'Total Number Provided',
    ],
    'Tracking Eligible': [
        'Tracking Eligible',
    ],
    'Training Class': [
        'Training Class',
    ],
    'Tuition': [
        'Tuition',
    ],
    'Tutoring': [
        'Tutoring',
    ],
    'Verification Date': [
        'Verification Date',
    ],
    'Visual Arts (Drawing, painting, etc)': [
        'Visual Arts (Drawing, painting, etc)',
    ],
    'Voucher Amendment Date': [
        'Voucher Amendment Date',
    ],
    'Voucher Award Date': [
        'Voucher Award Date',
    ],
    'Voucher Instance': [
        'Voucher Instance',
    ],
    'Voucher Status': [
        'Voucher Status',
    ],
    'We Rise eligibility': [
        'We Rise eligibility',
    ],
    'What are your career interests?': [
        'What are your career interests?',
    ],
    'What is the reason for this incentive?': [
        'What is the reason for this incentive?',
    ],
    'What is your current work eligibility status?': [
        'What is your current work eligibility status?',
    ],
    'What is your preferred language?': [
        'What is your preferred language?',
    ],
    'What type of transportation will you be using to get to work?': [
        'What type of transportation will you be using to get to work?',
    ],
    'Which industries interest you for an intership?': [
        'Which industries interest you for an intership?',
    ],
    'Which program sector are you interested in ?': [
        'Which program sector are you interested in ?',
    ],
    'Which program training are you interested in?': [
        'Which program training are you interested in?',
    ],
    'Work Experience': [
        'Work Experience',
    ],
    'Workforce Region': [
        'Workforce Region',
    ],
    'Worksite': [
        'Worksite',
    ],
    'Worksite Assignment': [
        'Worksite Assignment',
    ],
    'Worksite Department': [
        'Worksite Department',
    ],
    'Worksite Number/location': [
        'Worksite Number/location',
    ],
    'Year-Round Worksite': [
        'Year-Round Worksite',
    ],
    'Year-Round Worksite Duties': [
        'Year-Round Worksite Duties',
    ],
    'Youth Active in program?': [
        'Youth Active in program?',
    ],
    'Youth Match Status': [
        'Youth Match Status',
    ],
    'access_to_flexible_work_schedule': [
        'Access to flexible work schedule?',
    ],
    'access_to_healthcare_benefits': [
        'Access to healthcare benefits through employer?',
        'Does this position offer health insurance?',
        'Medical Benefits?',
    ],
    'access_to_other_benefits': [
        'Other fringe Benefits?',
    ],
    'access_to_other_insurance': [
        'Does this position offer other insurance (dental, life, vision, etc.)?',
    ],
    'access_to_pto': [
        'Access to PTO benefits through employer?',
        'Does this position offer paid time off (personal, sick, vacation, etc.)?',
    ],
    'access_to_retirement_benefits': [
        'Access to retirement benefits?',
        'Does this position offer a retirement plan (401K, pension, etc.)?',
    ],
    'access_to_sick_leave': [
        'Access to sick leave?',
    ],
    'access_to_training_through_employer': [
        'Access to additional training through employer?',
    ],
    'accomodations_training_and_employment': [
        'Describe needed accommodations for training and employment',
    ],
    'accountability_exit_status': [
        '935 Accountability Exit Status',
    ],
    'achieving_below_grade_level': [
        'Achieving below grade level',
    ],
    'actual_completion_date': [
        'Actual Completion Date',
    ],
    'adapatability_continuous_learning': [
        'Adaptability/Continuous Learning',
    ],
    'address_1': [
        'Address 1',
    ],
    'address_2': [
        'Address 2',
    ],
    'adult_services': [
        '903 Adult (WIOA)',
    ],
    'adults_in_household': [
        'Including yourself, how many adults (ages 18 and older) currently live in your household?',
    ],
    'age': [
        'Age',
        'Age at Program Start',
    ],
    'agreement_end_date': [
        'Agreement End Date',
    ],
    'app_id': [
        'App ID',
    ],
    'applicant_household_eligible_for': [
        'Applicant\'s household is eligible for',
    ],
    'application_date': [
        'Application Date',
    ],
    'application_status': [
        'Application Status',
    ],
    'apprenticeship_program': [
        '931 Registered Apprenticeship Program',
    ],
    'arrested_or_convicted_of_crime': [
        'Have you ever been arrested or convicted of a crime?',
        '801 Ex-Offender Status at Program Entry',
        'Offender',
        '801 Ex-Offender Status at Program Entry (WIOA)',
        'Have you ever been convicted of a crime?',
        'Have you ever been arrested?',
    ],
    'asbestos_work_experience': [
        'Asbestos Work Experience',
        'Automotive Work Experience',
    ],
    'assessment_date': [
        'Assessment Date',
    ],
    'basic_skills_deficient': [
        'Basic Skills Deficient',
        '804 Basic Skills Deficient/Low Levels of Literacy at Program Entry',
    ],
    'best_chance_eligibility': [
        'Best Chance eligibility',
    ],
    'blue_hills_zone': [
        'Blue Hills Zone',
    ],
    'books_and_supplies_amount': [
        'Books and Supplies',
    ],
    'business/organization_size': [
        'Business/Organization Size',
    ],
    'business_summary_mission': [
        'Business Summary/Mission',
    ],
    'cadd': [
        'CADD (Computer Aided Drafting and Design)',
    ],
    'cahp': [
        'CAHP',
    ],
    'career_awareness': [
        'Career Awareness',
    ],
    'career_connect': [
        'CareerConneCT',
    ],
    'career_exploration': [
        'Career Exploration',
    ],
    'career_interest': [
        'Career Interest',
    ],
    'career_interest_inventory': [
        'Career Interest Inventory',
    ],
    'career_pathways_interest': [
        'Career Pathways Interests',
    ],
    'carpentry_work_experience': [
        'Carpentry Work Experience',
    ],
    'case_number': [
        'Case Number',
    ],
    'cash_assistance': [
        'Cash Assistance',
    ],
    'cct_program_recommendation': [
        'Career ConneCT Program Recommendation',
    ],
    'change_related_to_training': [
        'Is this change related to training received?',
    ],
    'childcare': [
        'Childcare',
        'What types of support will you need to be successful in a training/workforce program: Childcare',
    ],
    'children_in_household': [
        'Including yourself, how many children (ages 17 and younger) currently live in your household?',
    ],
    'cip_training_1': [
        'Career ConneCT Training Provider CIP Code',
        'Training CIP Code',
    ],
    'cohort_enrollment_date': [
        'Cohort - Enrollment Date',
    ],
    'completed_returned_to_hs': [
        'Completed-Returned to HS',
    ],
    'counseling_services': [
        'Counseling Services',
    ],
    'credential_issuer': [
        'Credential Issuer',
    ],
    'credential_name': [
        'Credential Name',
    ],
    'credential_received': [
        'Credential Received',
    ],
    'credential_type_1': [
        '1800 Type of Recognized Credential (WIOA)',
        '1800 Type of Recognized Credential 1',
        'Credential 1 Type',
        'Credential Type',
        'Type of Recognized Credential 1',
    ],
    'credential_type_2': [
        '1802 Type of Recognized Credential #2 (WIOA)',
        '1802 Type of Recognized Credential 2',
        'Credential 2 Type',
        'Type of Recognized Credential 2',
    ],
    'credential_type_3': [
        '1804 Type of Recognized Credential #3 (WIOA)',
        '1804 Type of Recognized Credential 3',
        'Credential 3 Type',
        'Type of Recognized Credential 3',
    ],
    'credential_type_4': [
        'Credential 4 Type',
        'Type of Recognized Credential 4',
    ],
    'credential_type_5': [
        'Credential 5 Type',
        'Type of Recognized Credential 5',
    ],
    'credentials_obtained': [
        'Credentials Obtained',
    ],
    'cssd_referral': [
        'CSSD Referral',
    ],
    'cthires_id': [
        'CTHires State ID',
        'CTHires User ID',
    ],
    'cultural_barriers_at_program_entry': [
        '805 Cultural Barriers at Program Entry (WIOA)',
    ],
    'current_housing_situation_stable': [
        'Current Housing Situation Stable',
    ],
    'current_scholarship_amount': [
        'Current Scholarship Amount',
    ],
    'current_school': [
        'Current School',
        'School',
        'School or Program Name',
    ],
    'currently_attending': [
        'Are you currently attending?',
    ],
    'currently_needs_assistance_accomodations_for_training_and_employment': [
        'Currently Needs Assistance: Accommodations for Training and Employment',
    ],
    'currently_needs_assistance_acquiring_eligibility_documentation': [
        'Currently needs assistance: Acquiring Eligibility Documentation',
    ],
    'currently_needs_assistance_books_and_supplies': [
        'Currently Needs Assistance: Books and Supplies',
    ],
    'currently_needs_assistance_childcare': [
        'Currently Needs Assistance: Childcare',
    ],
    'currently_needs_assistance_complete_education_program_or_secure_and_maintain_employment': [
        'Needs additional assistance to complete an education program or secure and maintain employment',
    ],
    'currently_needs_assistance_educational_testing': [
        'Currently Needs Assistance: Educational Testing',
    ],
    'currently_needs_assistance_housing': [
        'Currently Needs Assistance: Housing',
    ],
    'currently_needs_assistance_legal_aid_services': [
        'Currently Needs Assistance: Legal Aid Services',
    ],
    'currently_needs_assistance_securing_food': [
        'Currently Needs Assistance: Securing Food',
    ],
    'currently_needs_assistance_tests_and_certifications': [
        'Currently Needs Assistance: Tests and Certifications',
    ],
    'currently_needs_assistance_transportation': [
        'Currently Needs Assistance: Transportation',
    ],
    'currently_needs_assistance_work_apparel_or_gear': [
        'Currently Needs Assistance: Work Apparel or Gear',
    ],
    'date_actual_dislocation': [
        '410 Date of Actual Dislocation',
    ],
    'date_attained_recognized_credential_4': [
        'Date Attained Recognized Credential 4',
    ],
    'date_attained_recognized_credential_5': [
        'Date Attained Recognized Credential 5',
    ],
    'date_change_occured': [
        'Date Change Occurred',
    ],
    'date_completed_mid_program_in_education_or_training_program_leading_to_credential_or_employment': [
        '1813 Date Completed During Program Participation an Education or Training Program Leading to a Recognized Credential or Employment',
        '1813 Date Completed, During Program Participation, an Education or Training Program Leading to a Recognized Postsecondary Credential or Employment (WIOA)',
    ],
    'date_contact_initiated': [
        'Dt_Contact_Initiated',
    ],
    'date_credential_1': [
        '1801 Date Attained Recognized Credential 1',
        '1801 Date Attained Recognized Credential (WIOA)',
    ],
    'date_credential_2': [
        '1803 Date Attained Recognized Credential #2 (WIOA)',
        '1803 Date Attained Recognized Credential 2',
    ],
    'date_credential_3': [
        '1805 Date Attained Recognized Credential #3 (WIOA)',
        '1805 Date Attained Recognized Credential 3',
    ],
    'date_enrolled_mid_program_in_education_or_training_program_leading_to_credential_or_employment': [
        '1811 Date Enrolled During Program Participation in an Education or Training Program Leading to a Recognized Credential or Employment',
        '1811 Date Enrolled During Program Participation in an Education or Training Program Leading to a Recognized Postsecondary Credential or Employment (WIOA)',
    ],
    'date_entered_training_1': [
        'Start Date',
        'Date Entered Training 1',
        '1302 Date Entered Training 1',
        'Training Start Date',
        'Date Entered Training',
        'Start Dt',
        '1302 Date Entered Training #1 (WIOA)',
    ],
    'date_entered_training_2': [
        'Date Entered Training 2',
        '1309 Date Entered Training 2',
        '1309 Date Entered Training #2',
        'Start Date_2',
    ],
    'date_entered_training_3': [
        'Date Entered Training 3',
        '1314 Date Entered Training 3',
        '1314 Date Entered Training #3',
    ],
    'date_first_dwg_service': [
        '933 Date of First DWG Service',
    ],
    'date_most_recent_contact': [
        'Dt_Successful_Contact',
    ],
    'date_of_birth': [
        'DOB',
        'Date of Birth',
        'birthday',
        '200 Date of Birth',
    ],
    'date_program_entry': [
        'Date of Program Entry',
        '900 Date of Program Entry',
        '900 Date of Program Entry (WIOA)',
    ],
    'date_program_exit': [
        '901 Date of Program Exit',
        '901 Date of Program Exit (WIOA)',
        'Date of Program Exit',
    ],
    'date_received_assessment_services': [
        '2103 Most Recent Date Received Assessment Services',
    ],
    'date_received_credential_1': [
        'Date Attained Recognized Credential 1',
        'Date Credential Attained',
        'Date Credential Obtained',
    ],
    'date_received_credential_2': [
        'Date Attained Recognized Credential 2',
    ],
    'date_received_credential_3': [
        'Date Attained Recognized Credential 3',
    ],
    'date_scheduled_orientation': [
        'Sched_Orientation_Dt',
    ],
    'date_skill_gains_educational_functioning_level': [
        '1806 Date of Most Recent Measurable Skill Gains: Educational Functioning Level (EFL) (WIOA)',
    ],
    'date_skill_gains_postsecondary_transcript_report_card': [
        '1807 Date of Most Recent Measurable Skill Gains: Postsecondary Transcript/Report Card (WIOA)',
    ],
    'date_skill_gains_secondary_transcript_report_card': [
        '1808 Date of Most Recent Measurable Skill Gains: Secondary Transcript/Report Card (WIOA)',
    ],
    'date_skill_gains_skills_progression': [
        '1810 Date of Most Recent Measurable Skill Gains: Skills Progression',
        '1810 Date of Most Recent Measurable Skill Gains: Skills Progression (WIOA)',
    ],
    'date_skill_gains_training_milestone': [
        '1809 Date of Most Recent Measurable Skill Gains: Training Milestone',
        '1809 Date of Most Recent Measurable Skill Gains: Training Milestone (WIOA)',
    ],
    'date_taken': [
        'Date Taken',
    ],
    'date_taken_service_delivery': [
        'Date Taken',
    ],
    'date_training_completed_1': [
        'Date Completed or Withdrew from Training 1',
        '1308 Date Completed or Withdrew from Training 1',
        'Training End Date',
        'Date Completed Training',
        '1308 Date Completed, or Withdrew from, Training #1',
        'End Date',
    ],
    'date_training_completed_2': [
        'Date Completed or Withdrew from Training 2',
        '1313 Date Completed or Withdrew from Training 2',
        '1313 Date Completed, or Withdrew from, Training #2',
        'End Date_2',
    ],
    'date_training_completed_3': [
        'Date Completed or Withdrew from Training 3',
        '1318 Date Completed or Withdrew from Training 3',
        '1318 Date Completed, or Withdrew from, Training #3',
    ],
    'days_in_training': [
        'Actual Days in Training',
    ],
    'detailed_status': [
        'Detailed Status',
    ],
    'disability': [
        'Disability',
        '203 Category of Disability',
        'Do you have a disability?',
        'Are you an ADS(Aging Disability Services) participant?',
        'Youth with a disability and / or special needs',
        '202 Individual with a Disability (WIOA)',
    ],
    'dislocated_worker': [
        '904 Dislocated Worker',
        '904 Dislocated Worker (WIOA)',
    ],
    'driver_license': [
        'Do you have a valid driver\'s license?',
        'Do you have an active driver\'s license?',
    ],
    'eligibility_1': [
        'Eligibility1',
    ],
    'eligibility_2': [
        'Eligibility2',
    ],
    'eligibility_3': [
        'Eligibility3',
    ],
    'employer': [
        'Employer',
        'Employer Name',
    ],
    'employer_entity_name': [
        'Entity Name',
    ],
    'employer_zip_code': [
        'Employer Zip Code',
        'Zip Code',
    ],
    'employment_and_training_services_related_to_snap': [
        '921 Employment and Training Services Related to SNAP',
    ],
    'employment_hours_worked': [
        'Average Hours per Week',
        'Hours',
    ],
    'employment_job_title': [
        'Job Title',
    ],
    'employment_match_method_1q_after_exit': [
        '1601 Type of Employment Match 1st Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_2q_after_exit': [
        '1603 Type of Employment Match 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_3q_after_exit': [
        '1605 Type of Employment Match 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_4q_after_exit': [
        '1607 Type of Employment Match 4th Quarter After Exit Quarter (WIOA)',
    ],
    'employment_naics': [
        'Occupation (NAICS) code',
        'NAICS 2 Digit Code',
        'NAICS 6 Digit Code',
        'NAICS 6 Digit Description',
    ],
    'employment_naics_q1': [
        '1614 Industry Code of Employment 1st Quarter After Exit Quarter',
    ],
    'employment_naics_q2': [
        '1615 Industry Code of Employment 2nd Quarter After Exit Quarter',
    ],
    'employment_naics_q3': [
        '1616 Industry Code of Employment 3rd Quarter After Exit Quarter',
    ],
    'employment_naics_q4': [
        '1617 Industry Code of Employment 4th Quarter After Exit Quarter',
    ],
    'employment_onet': [
        'O*NET Code',
    ],
    'employment_onet_q1': [
        'Occupational Code of Employment after Exit',
        'O*NET Code',
        '1610 Occupational Code (if available)',
    ],
    'employment_onet_q2': [
        'Occupational Code of Employment 2nd Quarter after Exit Quarter',
        '1612 Occupational Code of Employment 2nd Quarter After Exit Quarter (If available)',
    ],
    'employment_onet_q4': [
        'Occupational Code of Employment 4th Quarter after Exit Quarter',
        '1613 Occupational Code of Employment 4th Quarter After Exit Quarter (If available)',
    ],
    'employment_related_to_training_2q_after_exit': [
        '1608 Employment Related to Training (2nd Quarter After Exit) (WIOA)',
        'Employment Related to Training (2nd Quarter after Exit)',
    ],
    'employment_start_date': [
        'Job Start Date',
        '2118 Date Entered Employment',
        '2118 Date Entered Employment (Discretionary Grants)',
        'Start Date',
        'Employment Type',
        'Employment Start Date',
    ],
    'employment_status_2q_after_exit': [
        '1602 Employed in 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_3q_after_exit': [
        '1604 Employed in 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_4q_after_exit': [
        '1606 Employed in 4th Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_after_exit_q1': [
        '1600 Employed in 1st Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_at_exit': [
        'Employment Status at Exit',
        'Employment Status',
        'Employment Status at Placement End',
        'Completed-Employed',
        'Completed-Enrolled in PSEd or Adv Trng or Mil',
        'Outcome-Employed?',
    ],
    'employment_status_at_start': [
        'Are you currently employed?',
        'Employed at Enrollment',
        'Currently Working',
        'Employment Status at Intake',
        'employment_status',
        '400 Employment Status at Program Entry (WIOA)',
    ],
    'employment_town': [
        'Town',
    ],
    'end_date_funding': [
        'End Date',
    ],
    'end_reason': [
        'Why did this employment end?',
        'Non-Completion Exit Reason',
    ],
    'end_reason_for_funding_history': [
        'End Reason',
    ],
    'end_reason_for_training_record': [
        'Reason Did Not Complete',
    ],
    'english_language_learner': [
        'Are you an English language learner?',
        'English Language Learner',
        '803 English Language Learner at Program Entry (WIOA)',
    ],
    'enrolled_in_training_program': [
        'Did this individual enroll in a training program?',
    ],
    'enrollment_grade_level': [
        'Grade Level',
        'Current Grade',
        'Current Grade:',
        'Present Grade',
    ],
    'enrollment_gross_annual_income': [
        'What is your current gross annual household income (total income of all household members)?',
    ],
    'enrollment_start_date': [
        'Enrollment Date (start date)',
    ],
    'entered_non_traditional_employment': [
        '1611 Entered Non-Traditional Employment',
    ],
    'entered_training_related_employment': [
        '2126 Entered Training-Related Employment',
        '2126 Entered Training-Related Employment after Training Program Completion',
    ],
    'entrepreneurship': [
        'Entrepreneurial Education',
        'Entrepreneurship',
    ],
    'estimated_financial_aid': [
        'Estimated Financial Aid',
    ],
    'ethnicity': [
        'Hispanic or Latino (CWP)',
        'Ethnicity',
        'Hispanic or Latino',
        '210 Ethnicity: Hispanic / Latino (WIOA)',
    ],
    'experience_carpentry': [
        'experience_carpentry',
    ],
    'experience_drafting': [
        'experience_drafting',
    ],
    'experience_electrical': [
        'experience_electrical',
    ],
    'experience_enginerepair': [
        'experience_enginerepair',
    ],
    'experience_excel': [
        'experience_excel',
    ],
    'experience_generalrepairs': [
        'experience_generalrepairs',
    ],
    'experience_machining': [
        'experience_machining',
    ],
    'experience_painting': [
        'experience_painting',
    ],
    'experience_pipefitting': [
        'experience_pipefitting',
    ],
    'experience_planning': [
        'experience_planning',
    ],
    'experience_plastics': [
        'experience_plastics',
    ],
    'experience_rigging': [
        'experience_rigging',
    ],
    'experience_sheetmetal': [
        'experience_sheetmetal',
    ],
    'experience_sheetmetal_plastics': [
        'experience_sheetmetal_plastics',
    ],
    'experience_shipfitting': [
        'experience_shipfitting',
    ],
    'experience_welding': [
        'experience_welding',
    ],
    'final_scholarship_amount': [
        'Final Scholarship Amount',
    ],
    'financial_literacy': [
        'Financial Literacy',
    ],
    'financial_support': [
        'What types of support will you need to be successful in a training/workforce program: Financial Support',
    ],
    'first_job': [
        'First Job',
    ],
    'first_language_english': [
        'First Language English',
    ],
    'First Name': [
        'CTHires UserID',
        'First Name',
        'fname',
    ],
    'food': [
        'Food',
    ],
    'food_and_nutrition': [
        'What types of support will you need to be successful in a training/workforce program: Food and Nutrition',
    ],
    'foster_care': [
        'Foster Care/Ward of State',
        '704 Foster Care Youth Status at Program Entry (WIOA)',
    ],
    'funding_source': [
        'Funding Source',
        'Select the funding source.',
        'Funding',
    ],
    'funding_start_date?': [
        'Start Date',
    ],
    'gender': [
        'gender',
        'Gender Identity - Self-Identify',
        '201 Sex (WIOA)',
    ],
    'graduating_senior': [
        'Graduating Senior',
    ],
    'graduation_year': [
        'Graduation Year',
    ],
    'green_job': [
        'Is this a green job?',
    ],
    'gross_annual_income': [
        'Family Income',
        'Annualized Family Income',
    ],
    'hartford_promise_zone': [
        'Hartford Promise Zone',
    ],
    'have_you_been_impacted_by_covid_19?': [
        'Have you been impacted by COVID-19?',
    ],
    'head_of_household': [
        'Are you the head of household?',
    ],
    'healthcare': [
        'What types of support will you need to be successful in a training/workforce program: Healthcare',
    ],
    'high_passed': [
        'High_Passed',
    ],
    'high_school_diploma': [
        'High School Diploma or GED',
    ],
    'high_school_dropout': [
        'Are you a high school dropout?',
        'School Dropout',
    ],
    'highest_education_level_completed_at_program_entry': [
        'What is your highest level of post-secondary education completed?',
        'Highest Education Level Completed at Program Entry',
        'Highest Grade Completed',
        'highest_grade completed',
        '407 Highest School Grade Completed at Program Entry (WIOA)',
        'What is your highest level of grade school education completed?',
        'Last Grade Completed',
        'Highest Education Level Obtained',
        'Highest Level of Education at Intake',
        '408 Highest Educational Level Completed at Program Entry (WIOA)',
    ],
    'homeless_at_risk': [
        'Currently at Risk of Homelessness',
    ],
    'homeless_or_runaway': [
        'Are you currently homeless?',
        'Homeless',
        'Homeless at time of registration',
        'Runaway',
        '800 Homeless participant, Homeless Children and Youths, or Runaway Youth at Program Entry (WIOA)',
    ],
    'hourly_wage_at_exit': [
        'Hourly Wage',
        'Hourly Wage at Exit',
        'Hourly Earnings',
    ],
    'hourly_wage_at_worksite': [
        'Hourly Pay Rate',
    ],
    'hours_wk_2': [
        'Hours-Wk_2',
    ],
    'household_size': [
        'Total Family Members in Household (including yourself):',
        'Family Size',
    ],
    'housing': [
        'Housing',
        'What types of support will you need to be successful in a training/workforce program: Housing',
    ],
    'how_long_work_construction_and_what_did_you_do': [
        'How long did you work construction and what did you do?',
    ],
    'hps_credit_recovery_cohort': [
        'HPS Credit Recovery Cohort',
    ],
    'incentive_amount': [
        'What was the incentive value?',
    ],
    'incentive_form': [
        'What was the incentive form?',
    ],
    'incumbent_worker_advanced_to_new_position_1q_after_completion': [
        '2120 Incumbent Workers Advanced into a New Position with Current or New Employer in the 1st Quarter after Completion',
        '2120 Incumbent Workers Advanced into a New Position with Current or New Employer in the 1st Quarter after Training Program Completion',
    ],
    'incumbent_worker_advanced_to_new_position_2q_after_completion': [
        '2121 Incumbent Workers Retained Current Position in the 2nd Quarter after Training Program Completion',
        '2122 Incumbent Workers Advanced into a New Position with Current Employer or New Employer in the 2nd Quarter after Training Program Completion',
        '2122 Incumbent Workers Advanced into a New Position with Current or New Employer in the 2nd Quarter after Training Program Completion',
    ],
    'incumbent_worker_advanced_to_new_position_3q_after_completion': [
        '2123 Incumbent Workers Retained Current Position in the 3rd Quarter after Training Program Completion',
        '2124 Incumbent Workers Advanced into a New Position with Current or New Employer in the 3rd Quarter after Training Program Completion',
    ],
    'incumbent_worker_retained_position': [
        '2119 Incumbent Workers Retained Current Position',
    ],
    'incumbent_worker_retained_position_1q_after_completion': [
        '2119 Incumbent Workers Retained Current Position in the 1st Quarter after Training Program Completion',
    ],
    'incumbent_worker_training': [
        '907 Recipient of Incumbent Worker Training',
    ],
    'initial_scholarship_amount': [
        'Initial Scholarship Amount',
    ],
    'interested_in_employment_search_support': [
        'Interested in: Employment Search Support',
    ],
    'interested_working_outside': [
        'Are you interested in working outside?',
    ],
    'interested_working_with_computers': [
        'Are you interested in working with computers?',
    ],
    'interested_working_with_dress_code_in_professional_setting': [
        'Are you interested in working with a dress code in a professional setting?',
    ],
    'jfes': [
        'Currently Enrolled in JFES',
        'JFES',
    ],
    'job_readiness': [
        'Job Readiness',
    ],
    'job_shadowing': [
        'Job Shadowing',
    ],
    'job_title': [
        'Job Title',
    ],
    'job_title_2': [
        'Job Title_2',
    ],
    'justice_involved': [
        'Justice-Involved',
        'Justice Involved',
    ],
    'last_date_of_employment': [
        'What was the last date of employment?',
    ],
    'Last Name': [
        'Last Name',
        'lname',
    ],
    'leadership_development': [
        'Leadership Development',
        'Leadership Dev',
    ],
    'legal_aid': [
        'What types of support will you need to be successful in a training/workforce program: Legal Aid',
    ],
    'legally_allowed_to_work_in_us': [
        'Are you legally allowed to work in the United States?',
        'Are you legally allowed to work in US?',
        'Legally Allowed to Work in US',
    ],
    'level_up_referral': [
        'Level Up Referral',
    ],
    'long_term_unemployed_at_program_entry': [
        'Has the participant been unemployed for 27 or more consecutive weeks?',
        '402 Long-Term Unemployed at Program Entry (WIOA)',
    ],
    'longest_employed_with_one_employer': [
        'What is the longest amount of time you have worked for an employer?',
    ],
    'low_income': [
        'Does the participant qualify as low income?',
        'Low Income',
        'Meets Definition of Low Income',
        '802 Low Income Status at Program Entry (WIOA)',
    ],
    'lunch_status': [
        'Eligible Free Lunch',
        'Lunch Status',
    ],
    'manufacturing_experience': [
        'manufacturing_experience',
    ],
    'marital_status': [
        'Marital Status',
    ],
    'mental_health': [
        'Mental Health',
    ],
    'mentoring': [
        'Mentoring',
    ],
    'middle_name': [
        'Middle',
        'Middle Initial',
    ],
    'migrant_and_seasonal_farmworker': [
        '808 Eligible Migrant and Seasonal Farmworker Status (WIOA sec. 167)',
    ],
    'monitoring_status': [
        'Monitoring Status',
    ],
    'most_recent_date_basic_career_services': [
        '1003 Most Recent Date Received Basic Career Services (Staff-Assisted)',
    ],
    'most_recent_date_follow_up_service': [
        '1503 Most Recent Date Received Follow-up Service',
    ],
    'most_recent_date_supportive_services': [
        '1409 Most Recent Date Received Supportive Services',
    ],
    'most_recent_job_days_employed': [
        'Days Employed',
    ],
    'most_recent_job_hourly_wage': [
        'For your most recent job, what was your hourly wage?',
        'Hourly Wage in Most Recent Employment Prior to Participation',
    ],
    'most_recent_job_hours_worked': [
        'For your most recent job, how many hours did you work each week, on average?',
        'Hours Worked per Week Most Recent Employment Prior to Participation',
        'Hours Worked per Week',
        'Weekly Hours (Est.)',
    ],
    'most_recent_job_industry': [
        'For your most recent job, what was the industry?',
    ],
    'most_recent_job_last_date_of_employment': [
        'For your most recent job, what was your last date of employment?',
    ],
    'most_recent_job_onet': [
        'Enter O*NET code for most recent job.',
        'Occupational Code of Most Recent Employment Prior to Participation',
        '403 Occupational Code of Most Recent Employment Prior to Participation (if available)',
    ],
    'most_recent_job_title': [
        'For your most recent job, what was the job title?',
    ],
    'most_recent_sye_participation': [
        'Most Recent SYE Participation',
    ],
    'naics': [
        'Industry',
    ],
    'national_dislocated_workers_grant': [
        '932 National Dislocated Worker Grants (DWG)',
    ],
    'occupational_skills_training': [
        'Occupational Skills Training',
        'Occupational Skills Trng',
    ],
    'onet_training_1': [
        'Occupational Skills Training Code 1',
        '1306 Occupational Skills Training Code 1',
        'O*NET Code',
        'O*NET-SOC Code (XX-XXXX.XX)',
        '1306 Occupational Skills Training Code #1',
    ],
    'onet_training_2': [
        'Occupational Skills Training Code 2',
        '1311 Occupational Skills Training Code 2',
        '1311 Occupational Skills Training Code #2',
    ],
    'onet_training_3': [
        'Occupational Skills Training Code 3',
        '1316 Occupational Skills Training Code 3',
        '1316 Occupational Skills Training Code #3',
    ],
    'organization': [
        'Organization',
    ],
    'orientation_s_or_ns': [
        'Orientation S or NS',
    ],
    'other_barriers_1': [
        'Other Barrier (1)',
        'Other Barriers',
    ],
    'other_barriers_2': [
        'Other Barrier (2)',
    ],
    'other_public_assistance_recipient': [
        '604 Other Public Assistance Recipient',
    ],
    'other_reasons_for_exit': [
        '923 Other Reasons for Exit',
        '923 Other Reasons for Exit (WIOA)',
    ],
    'other_supportive_services': [
        'Other Supportive Services',
    ],
    'other_work/trade_certifications': [
        'Do you have any other work or trade certifications? If yes, please explain.',
    ],
    'paid_competency_training_hours': [
        'Paid Competency Training Hours',
    ],
    'paid_worksite_hours': [
        'Paid Worksite Hours',
    ],
    'parent_or_pregnant': [
        'Are you currently a parent?',
        'Pregnant or Parent',
        'Applicant\'s household is pregnant or is a custodial parent',
        '701 Pregnant or Parenting Youth',
        'Parent',
    ],
    'past_participant_in_cyep': [
        'Past Participant in CYEP',
    ],
    'pathways': [
        'Pathways',
    ],
    'permit_or_driver_license': [
        'Currently Has Learnerâ€™s Permit or Driverâ€™s License',
    ],
    'placement_made_through_program': [
        'Was this placement made through this program?',
    ],
    'portal_application_date': [
        'Portal application Date',
    ],
    'post_secondary_transition_activities': [
        'Post-Secondary Transition Activities',
    ],
    'pre_apprenticeship': [
        'Pre-apprenticeship',
    ],
    'primary_funding': [
        'Primary Funding',
    ],
    'primary_funding_other': [
        'Primary Funding-Other',
    ],
    'primary_training_funding': [
        'Primary Training Funding',
    ],
    'primary_type_training_service_for_training_activity_1': [
        '2109 Primary Type of Training Service for Training Activity 1',
    ],
    'primary_type_training_service_for_training_activity_2': [
        '2112 Primary Type of Training Service for Training Activity 2',
    ],
    'primary_type_training_service_for_training_activity_3': [
        '2115 Primary Type of Training Service for Training Activity 3',
    ],
    'program_operator': [
        'Program Operator',
    ],
    'provider': [
        'Provider',
    ],
    'race/ethnicity': [
        'Race Ethnicity',
        '211 American Indian / Alaska Native (WIOA)',
        'Race1',
        'Race2',
        'Race3',
        'Race4',
        'Race (CWP)',
        'Race - Self-Identify',
        'What is your race? Select one or more:',
        'Race',
        '212 Asian (WIOA)',
        '213 Black / African American (WIOA)',
        '214 Native Hawaiian / Other Pacific Islander (WIOA)',
        '215 White (WIOA)',
    ],
    'rapid_response': [
        '908 Rapid Response',
    ],
    'rapid_response_additional_assistance': [
        '909 Rapid Response (Additional Assistance)',
    ],
    'received_needs_related_payments': [
        '1500 Received Needs-Related Payments',
    ],
    'received_training': [
        'Received Training',
        '1300 Received Training',
        '1300 Received Training (WIOA)',
    ],
    'receiving_dcf_or_foster_care_services': [
        'Foster Care or DCF',
        'Appliciant is receiving DCF Services',
        'DCF Involved',
    ],
    'referral_source': [
        'referral_source',
    ],
    'registered_apprenticeship': [
        'Is this a registered apprenticeship?',
    ],
    'registered_selective_service': [
        'Are you registered for selective service?',
    ],
    'registration_submission_date': [
        'Registration Submitted Date:',
    ],
    'reliable_transportation': [
        'Do you have reliable transportation?',
        'Do you have trouble getting to work?',
    ],
    'resume': [
        'Resume',
    ],
    'retention_with_same_employer_2q_and_4q': [
        '1618 Retention with the same employer in the 2nd Quarter and the 4th Quarter (WIOA)',
    ],
    'saga': [
        'Do you currently receive, or have you received in the past six months, any of the following: State Administered General Assistance',
        'Do you currently receive, or have you received in the past six months: State Adminstered General Assistance',
    ],
    'sasid': [
        'SASID',
    ],
    'scheduled_end_date': [
        'Scheduled End Date',
        'Projected End Date',
        'Est End Dt',
    ],
    'scheduled_start_date': [
        'Scheduled Start Date',
        'Agreement Start Date',
        'Est Start Dt',
    ],
    'school_status_at_exit': [
        'School Status at Exit',
        'Education Status at Placement End',
    ],
    'school_status_at_program_entry': [
        'College Status',
        'Education Status at Intake',
        'Education Status',
        'Are you currently enrolled in an education program?',
        'School Status at Program Entry',
        'Are you currently enrolled in and attending an education program?',
        'School Status at time of registration',
        '409 School Status at Program Entry (WIOA)',
    ],
    'secondary_funding': [
        'Secondary Funding',
    ],
    'secondary_funding_other': [
        'Secondary Funding-Other',
    ],
    'secondary_type_training_service_for_training_activity_1': [
        '2110 Secondary Type of Training Service for Training Activity 1',
    ],
    'secondary_type_training_service_for_training_activity_2': [
        '2113 Secondary Type of Training Service for Training Activity 2',
    ],
    'secondary_type_training_service_for_training_activity_3': [
        '2116 Secondary Type of Training Service for Training Activity 3',
    ],
    'sector': [
        'Sector',
    ],
    'selective_service': [
        'Selective Service',
    ],
    'servsafe_certified': [
        'Are you ServSafe certified?',
    ],
    'single_parent': [
        'Are you a single parent?',
        '806 Single Parent at Program Entry (WIOA)',
    ],
    'snap': [
        'Food Stamps',
        'Receipt of SNAP',
        'Do you currently receive, or have you received in the past six months: Supplemental Nutrition Assistance Program',
        'Do you currently receive Supplemental Nutrition Assistance Program?',
        'Do you currently receive, or have you received in the past six months, any of the following: Supplemental Nutrition Assistance Program',
        'Currently Receiving SNAP or Other Nutrition Supports',
        'SNAP',
        '603 Supplemental Nutrition Assistance Program (SNAP)',
    ],
    'snap_tanf_saga': [
        'Applicant\'s household currently receives SNAP/TFA/SAGA',
    ],
    'special_requirement': [
        'Please Specify Other Special Requirement',
    ],
    'ssi/ssdi': [
        'Do you currently receive, or have you received in the past six months: Supplemental Security Income',
        'Do you currently receive, or have you received in the past six months: Social Security Disability Income',
        'Do you currently receive, or have you received in the past six months, any of the following: Social Security Disability Income',
        'Do you currently receive, or have you received in the past six months, any of the following: Supplemental Security Income',
    ],
    'ssi_ssdi': [
        'SSI/SSD',
        'SSI or SSDI',
        '602 Supplemental Security Income(SSI) / Social Security Disability Insurance (SSDI)',
    ],
    'ssn': [
        'Social Security #',
        '2700 Social Security Number',
        'Social Security Number',
        'SSN',
    ],
    'state': [
        'State',
        '101 State Code of Residence (WIOA)',
    ],
    'substance_use': [
        'Substance Use',
    ],
    'suffix': [
        'Suffix',
    ],
    'summer_program_end_date': [
        'Summer Program Exit Date',
    ],
    'summer_program_start_date': [
        'Summer Program Start Date',
    ],
    'support_type': [
        'Support Type',
    ],
    'support_value': [
        'Support Value',
    ],
    'supports_other': [
        'Supports-Other',
    ],
    'supports_provided_1': [
        'Supports Provided',
    ],
    'supports_provided_2': [
        'Supports Provided-Other',
    ],
    'tanf': [
        'Receipt of TANF',
        'Do you currently receive, or have you received in the past six months: Temporary Family Assistance',
        'Do you currently receive, or have you received in the past six months, any of the following: Temporary Family Assistance',
        'Does the participant qualify for TANF?',
        '600 Temporary Assistance to Needy Families (TANF)',
        '601 Exhausting TANF Within 2 Years (Part A Title IV of the Social Security Act) at Program Entry (WIOA)',
    ],
    'tertiary_type_training_service_for_training_activity_1': [
        '2111 Tertiary Type of Training Service for Training Activity 1',
    ],
    'tertiary_type_training_service_for_training_activity_2': [
        '2114 Tertiary Type of Training Service for Training Activity 2',
    ],
    'tertiary_type_training_service_for_training_activity_3': [
        '2117 Tertiary Type of Training Service for Training Activity 3',
    ],
    'test_score': [
        'Test Score',
    ],
    'third_funding': [
        'Third Funding',
    ],
    'third_funding_other': [
        'Third Funding-Other',
    ],
    'ticket_to_work': [
        'Do you currently receive, or have you received in the past six months: Ticket to Work',
        'Do you currently receive, or have you received in the past six months, any of the following: Ticket to Work',
    ],
    'total_program_costs': [
        'Total Program Costs',
    ],
    'town_person': [
        'city',
        'Town/Region',
        'Town at Intake',
        '102 County Code',
        'Town of Residence',
        'City, State County',
        '102 County Code of Residence',
    ],
    'training_1': [
        'Training Name',
        'training_1',
    ],
    'training_1_area': [
        'Training Area',
    ],
    'training_1_category': [
        'Training Category',
    ],
    'training_2': [
        'training_2',
    ],
    'training_3': [
        'training_3',
    ],
    'training_completed_1': [
        'Training Completed 1',
        '1307 Training Completed 1',
        'Training Completion Status',
        'Completion Status',
        'Training Completed',
        '1307 Training Completed #1',
    ],
    'training_completed_2': [
        'Training Completed 2',
        '1312 Training Completed 2',
        '1312 Training Completed #2',
    ],
    'training_completed_3': [
        'Training Completed 3',
        '1317 Training Completed 3',
        '1317 Training Completed #3',
    ],
    'training_end_date': [
        'End Date',
        'Actual End Date',
        'Program End',
        'End Dt',
    ],
    'training_format': [
        'Training Format',
    ],
    'training_job_title': [
        'Job Title',
        'Title',
    ],
    'training_program_id': [
        'Training Program ID',
    ],
    'training_provider': [
        'Career ConneCT Training Provider',
        'Training Provider Name',
        'Training Program Name',
        'College or Training Program Name',
        'Training Provider',
        'Provider',
        'School or Program Name',
        'Youth Provider',
        'Career ConneCT Training Provider Program of Study 1',
    ],
    'training_wages': [
        'Wage-Hr',
    ],
    'training_weekly_hours': [
        'Total Hours',
        'Hours-Wk',
    ],
    'transportation': [
        'Transportation',
        'What types of support will you need to be successful in a training/workforce program: Transportation',
    ],
    'type_of_crime': [
        'What type of crime was it?',
    ],
    'type_service': [
        'Type of Supportive Service',
    ],
    'type_training_1': [
        'Type of Training Service 1',
        '1303 Type of Training Service 1',
        'Type of Training',
        '1303 Type of Training Service #1 (WIOA)',
    ],
    'type_training_2': [
        'Type of Training Service 2',
        '1310 Type of Training Service 2',
        '1310 Type of Training Service #2 (WIOA)',
    ],
    'type_training_3': [
        'Type of Training Service 3',
        '1315 Type of Training Service 3',
        '1315 Type of Training Service #3 (WIOA)',
    ],
    'underemployed': [
        'If you are currently employed, are you underemployed?',
        'If you are employed, are you currently underemployed?',
        '2101 Underemployed Worker',
    ],
    'unemployment_compensation': [
        '401 UC Eligible Status',
        'If you are not employed, are you currently receiving unemployment compensation?',
    ],
    'veteran_status': [
        'Are you a veteran?',
        'Veteran',
        'veteran_status',
        '300 Veteran Status',
    ],
    'wage_hr_2': [
        'Wage-Hr_2',
    ],
    'wages_1q_after_exit': [
        '1703 Wages 1st Quarter After Exit Quarter (WIOA)',
    ],
    'wages_1q_prior': [
        '1702 Wages 1st Quarter Prior to Participation Quarter',
    ],
    'wages_2q_after_exit': [
        '1704 Wages 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'wages_2q_prior': [
        '1701 Wages 2nd Quarter Prior to Participation Quarter',
    ],
    'wages_3q_after_exit': [
        '1705 Wages 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'wages_3q_prior': [
        '1700 Wages 3rd Quarter Prior to Participation Quarter',
    ],
    'wages_4q_after_exit': [
        '1706 Wages 4th Quarter After Exit Quarter (WIOA)',
    ],
    'wages_after_exit': [
        'Hourly Wage',
        'Wage',
    ],
    'wagner_peyser_employment_service': [
        '918 Wagner-Peyser Employment Service (WIOA)',
    ],
    'week_end_date': [
        'Week Ending Date',
    ],
    'week_ending_date': [
        'Week Ending Date',
    ],
    'which_services_would_be_helpful': [
        'Which supportive services would you find helpful?',
    ],
    'wioa_id': [
        '100 Unique Individual Identifier (WIOA)',
    ],
    'work_site': [
        'Work Site',
    ],
    'work_site_town': [
        'Work Site Town',
    ],
    'work_supports': [
        'Work Supports',
    ],
    'workforce_board_code': [
        'Local Workforce Board Code',
    ],
    'worksite_2': [
        'Work Site_2',
    ],
    'worksite_end_date': [
        'Job End Date',
    ],
    'worksite_total_hours': [
        'Total Hours',
    ],
    'worksite_town': [
        'Work Site Town_2',
    ],
    'year_of_graduation': [
        'Year of Graduation:',
    ],
    'year_round_program_end_date': [
        'Year-Round Program End Date',
    ],
    'year_round_program_start_date': [
        'Year-Round Program Start Date',
    ],
    'youth_needs_additional_assistance': [
        '702 Youth Who Needs Additional Assistance',
    ],
    'youth_placement_2q': [
        '1900 Youth 2nd Quarter Placement (Title I) (WIOA)',
    ],
    'youth_placement_4q': [
        '1901 Youth 4th Quarter Placement (Title I) (WIOA)',
    ],
    'youth_services': [
        '905 Youth (WIOA)',
    ],
    'zip_code': [
        'Zip Code at Intake',
        'Zip Code',
        'zip',
        '103 Zip Code of Residence',
    ],
}

# 2) Accepted responses with types: { user_friendly_name: {'type': [...], 'accepted_responses': [...]} }
simple_format_pa25_119_data_accepted_responses_w_types = {
    '1001 Date of First Basic Career Service (Staff-Assisted)': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1004 Date of Most Recent Career Service (WIOA)': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1007 Date of Most Recent Reportable Individual Contact': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '105 Special Project ID - 1': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '106 Special Project ID - 2': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '107 Special Project ID - 3': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1200 Date of First Individualized Career Service': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1201 Most Recent Date Received Individualized Career Service': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1205 Type of Work Experience': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '12_month_date_benchmark': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '12_months_employed': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '1328 Training Provided Virtual/Online': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1331 Training Leading to an Associate Degree': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1332 Participated in Postsecondary Education During Program Participation': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 3,
    },
    '1332 Participated in Postsecondary Education During Program Participation (WIOA)': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1333 Received Private Sector Training': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '1333 Received training from program(s) operated by the private sector': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '1401 Enrolled in Secondary Education Program (WIOA)': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    '18_month_date_benchmark': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '18_months_employed': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '24_month_date_benchmark': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '24_months_employed': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '6_month_date_benchmark': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '6_months_employed': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    '807 Displaced Homemaker at Program Entry (WIOA)': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'Apt. Floor': {
        'type': '',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'CATDLP': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'CATP': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'CDS eligibility': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'CNA Certified Nursing Assistant - currently hold': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'CTHires State ID': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Certification appointment date': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Certification appointment location': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Citizenship': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Closure Date': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'Co-Enrolled': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Co-funded': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Communication': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Completed80PercProg': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Contact Location or Method': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Contextualized Education': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Core Services to Employers': {
        'type': '',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Cover Letter': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Cover Letter Completed': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Critical Thinking/Problem Solving': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Culinary Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Currently Enrolled in WIOA': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Career ConneCT; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Customer Service': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Dancing': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Data Entry/Typing WPM': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Date Co-Enrolled': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Date Referral Made': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'Date Status Updated': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'Date Taken': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'Deobligation Amount': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Developed By': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Did this individual enter new employment?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Did youth attend Job Readiness Training?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Diversity and Inclusion': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Do you currently receive, or have you received in the past six months, any of the following?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Do you have an LLC?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Do you have an updated resume?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Do you have medical insurance?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Do you have stable housing?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Do you have your high school credential (diploma or GED)?': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Do you own a vehicle?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Do you speak a language, other than English, If so what?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Drywall Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'EB': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'EB_Job Title': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'EB_JobOfferSTatus': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'EB_Start_Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'EB_Step': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'EB_Wage': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Electrical Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Email': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Employment Management (Job Seeking)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Employment Readiness': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Engagement and Employer Onboarding': {
        'type': '',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Enrolled': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Entity Subtype': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Entity Type': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Entity Unique Identifier': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Estimated Days in Training': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'Estimated Number of Slots': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Final Placement Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'First Referral Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'General Construction Labor Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'General Professionalism': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'HVAC Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Have you attended any college or post-high school training?': {
        'type': 'identifier',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Have you ever been incarcerated?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Have you ever owned a business?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Have you ever worked on a construction site?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Have you participated in Summer Youth Program before?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Head of Household': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'High School Diploma / GED': {
        'type': 'identifier',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Hire Count': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Hire Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Hired Permanently?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Hired by Worksite': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'How did you hear about this program?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 8,
    },
    'How many college credits have you earned?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'How proficient are you with this language?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Identifier': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'OWS Basic Skills Remediation; WIOA Youth Recruitment; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'If Other, please specify:': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If earn and learn, type': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If employed, did participant report hourly salary?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If other, describe': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If yes, how many years did you complete?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If yes, where and what did you do?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If yes, where?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'If you are attending college, Will you be going to college in fall?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'IfNo-TerminationReason': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'In the last 5 years, have you had an OSHA license?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Installation or Insulation Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Intake Statuses': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'Interested in: Computer Literacy': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Interested in: Interview Preparation': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Interested in: Resume Support': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Interested in: Training': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Internet Search': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Interpersonal/Collaboration and Teamwork': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Interview Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Is the vehicle registered and insured?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Is this active military service?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'Is this job related to training received?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'JD End': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'JD Exit Reason': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'JD Start': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Job Application': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Job Description': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Job Developer': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Job Market': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Job Referral': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Job Search': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Jobs Funnel eligibility': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'LPN Licensed Practical Nurse - currently hold': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Labor Market and Employment Information Services are split across three areas.': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Landscaping Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Last Modified': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Length of Agreement (Days)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Low_AJC': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'MA Medical Assistant': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'MPI Youth': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Managing Region': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'OWS Basic Skills Remediation; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Manufacturing Machinist or CNC Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Masonry Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Medium_Remediation': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Member of Populations': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Microsoft Word, PowerPoint, Excel': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Mock Interview': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'NAACP eligibility': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'New Skills Acquired (select all that apply)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'No Longer Available': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Number of Slots Filled': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Office Equipment (i.e. copier, fax machine, scanner, etc.)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Other': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways; CYEP',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'Other Costs': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Other Program Recommendation': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Other Skills (NAICS code)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'PY15': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY16': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY17': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY18': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY19': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY20': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY21': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY22': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY23': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY24': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'PY25': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'Painting Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Parent or Corporate Entity': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Participant Site Identifier': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Participant Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Partnership Activities': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Payroll Type': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Pell Grant': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Permanently Closed': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Phone Number': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Placed at Worksite?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Plays an instrument': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Plumbing Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Position': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Post-Secondary Plans': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Prefix': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Professionalism': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Program Vendor': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Projected Completion Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Pronouns': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'Prove IT': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Quadrant of Residency': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'RN Registered Nurse - currently hold': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Reason for Referral': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'Reason for Unfilled Slots': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Reference Letters Completed': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Referral Closed': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Referral Count': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Referral Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'Referral to Workshop or Service': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Referred To': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'Registration Season(s)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Registration Year': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Registration Year:': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Reporting Complete': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Resume Completed': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Resume Creation': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Resume Critique': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Resume Revision': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Secondary Education': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'SiMentor': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Special Requirements (check all that apply)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Specify Other Post-Secondary Plans': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Specify Workshop or Service': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Spoken Word or Poetry': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Status Change': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Status Change Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Street Address': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Student Key': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Subsidized Loans': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Summer Duties': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Summer Worksite': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Swimming': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Technology/Digital Literacy': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Test Score': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'OWS Basic Skills Remediation; WIOA Youth Recruitment; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'Tests and Fees': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Tier': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Time/Self-Management': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Total Number Provided': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; Good Jobs; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; CYEP; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth',
        'grouped_col_name': '',
        'program_count': 37,
    },
    'Tracking Eligible': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Training Class': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Tuition': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Tutoring': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Verification Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 9,
    },
    'Visual Arts (Drawing, painting, etc)': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Voucher Amendment Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Voucher Award Date': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Voucher Instance': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Voucher Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'We Rise eligibility': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'What are your career interests?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'What is the reason for this incentive?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'What is your current work eligibility status?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'What is your preferred language?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'What type of transportation will you be using to get to work?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Which industries interest you for an intership?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Which program sector are you interested in ?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'Which program training are you interested in?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Work Experience': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Workforce Region': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Worksite': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'Worksite Assignment': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Worksite Department': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Worksite Number/location': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Year-Round Worksite': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Year-Round Worksite Duties': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Youth Active in program?': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'Youth Match Status': {
        'type': '',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'access_to_flexible_work_schedule': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'access_to_healthcare_benefits': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'access_to_other_benefits': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'access_to_other_insurance': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'access_to_pto': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'access_to_retirement_benefits': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'access_to_sick_leave': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'access_to_training_through_employer': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Good Jobs',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'accomodations_training_and_employment': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'accountability_exit_status': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'achieving_below_grade_level': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'actual_completion_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'end_date',
        'program_count': 2,
    },
    'adapatability_continuous_learning': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'address_1': {
        'type': '',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'address_2': {
        'type': '',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'adult_services': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'adults_in_household': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 8,
    },
    'age': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); CYEP',
        'grouped_col_name': 'age',
        'program_count': 2,
    },
    'agreement_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'app_id': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'applicant_household_eligible_for': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'application_date': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': 'start_date',
        'program_count': 1,
    },
    'application_status': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'start_status',
        'program_count': 8,
    },
    'apprenticeship_program': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'arrested_or_convicted_of_crime': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; HFPG, UW; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 10,
    },
    'asbestos_work_experience': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'assessment_date': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': 'start_date',
        'program_count': 1,
    },
    'basic_skills_deficient': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 13,
    },
    'best_chance_eligibility': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'blue_hills_zone': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'books_and_supplies_amount': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': 'services_amount',
        'program_count': 4,
    },
    'business/organization_size': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'previous_job',
        'program_count': 13,
    },
    'business_summary_mission': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'cadd': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'cahp': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'career_awareness': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'career_connect': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'career_exploration': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'career_interest': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'career_interest_inventory': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'career_pathways_interest': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'carpentry_work_experience': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'case_number': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'cash_assistance': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'supports',
        'program_count': 1,
    },
    'cct_program_recommendation': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'change_related_to_training': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 9,
    },
    'childcare': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP; HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'children_in_household': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 8,
    },
    'cip_training_1': {
        'type': 'CIPCode',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Good Jobs',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'cohort_enrollment_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'completed_returned_to_hs': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'counseling_services': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'credential_issuer': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'credential_name': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'credential_received': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'credential_type_1': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth',
        'grouped_col_name': '',
        'program_count': 41,
    },
    'credential_type_2': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Good Jobs; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 6,
    },
    'credential_type_3': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Good Jobs; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 6,
    },
    'credential_type_4': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Good Jobs; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'credential_type_5': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Good Jobs; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'credentials_obtained': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'cssd_referral': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'cthires_id': {
        'type': 'identifier',
        'Section': 'Unmatched; Section A - Individual Information',
        'programs': 'Manufacturing Pipeline; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 14,
    },
    'cultural_barriers_at_program_entry': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'current_housing_situation_stable': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'current_scholarship_amount': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'current_school': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; CYEP; State Youth Employment Programs (OYE, DCF, DADS); CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'currently_attending': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_accomodations_for_training_and_employment': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_acquiring_eligibility_documentation': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_books_and_supplies': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_childcare': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_complete_education_program_or_secure_and_maintain_employment': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_educational_testing': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_housing': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_legal_aid_services': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_securing_food': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_tests_and_certifications': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_transportation': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'currently_needs_assistance_work_apparel_or_gear': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_actual_dislocation': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'date_attained_recognized_credential_4': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_attained_recognized_credential_5': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_change_occured': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 9,
    },
    'date_completed_mid_program_in_education_or_training_program_leading_to_credential_or_employment': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_contact_initiated': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_credential_1': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_credential_2': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_credential_3': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_enrolled_mid_program_in_education_or_training_program_leading_to_credential_or_employment': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_entered_training_1': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; Manufacturing Pipeline; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 44,
    },
    'date_entered_training_2': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project; CYEP',
        'grouped_col_name': '',
        'program_count': 6,
    },
    'date_entered_training_3': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'date_first_dwg_service': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_most_recent_contact': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_of_birth': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; Manufacturing Pipeline; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': 'age',
        'program_count': 52,
    },
    'date_program_entry': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'date_program_exit': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'date_received_assessment_services': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': 'date_services',
        'program_count': 1,
    },
    'date_received_credential_1': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; WIOA Adult, WIOA Dislocated Worker, JFES; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth',
        'grouped_col_name': '',
        'program_count': 40,
    },
    'date_received_credential_2': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_received_credential_3': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_scheduled_orientation': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_skill_gains_educational_functioning_level': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_skill_gains_postsecondary_transcript_report_card': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_skill_gains_secondary_transcript_report_card': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'date_skill_gains_skills_progression': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_skill_gains_training_milestone': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'date_taken': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; HFPG, UW; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Recruitment; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 14,
    },
    'date_taken_service_delivery': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'date_training_completed_1': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; Congressional Direct Spending/Community Project; CYEP',
        'grouped_col_name': '',
        'program_count': 37,
    },
    'date_training_completed_2': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project; CYEP',
        'grouped_col_name': '',
        'program_count': 6,
    },
    'date_training_completed_3': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'days_in_training': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'detailed_status': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'disability': {
        'type': 'categorical',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project; OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 16,
        'accepted_responses': DISABILITY_MAPPING
    },
    'dislocated_worker': {
        'type': 'categorical',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
        'accepted_responses': DISLOCATED_WORKER_MAPPING
    },
    'driver_license': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'barriers',
        'program_count': 3,
    },
    'eligibility_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'eligibility_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'eligibility_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employer': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Good Jobs; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Manufacturing Pipeline; WIOA Adult, WIOA Dislocated Worker, JFES; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'employer',
        'program_count': 13,
    },
    'employer_entity_name': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'employer',
        'program_count': 13,
    },
    'employer_zip_code': {
        'type': 'zipCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'employer',
        'program_count': 13,
    },
    'employment_and_training_services_related_to_snap': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_hours_worked': {
        'type': 'hoursWorked',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'employment_job_title': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; WIOA Adult, WIOA Dislocated Worker, JFES; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'employment_match_method_1q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_match_method_2q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_match_method_3q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_match_method_4q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_naics': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'employment_naics_q1': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_naics_q2': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_naics_q3': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_naics_q4': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_onet': {
        'type': 'ONETCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 9,
    },
    'employment_onet_q1': {
        'type': 'ONETCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; WIOA Adult, WIOA Dislocated Worker, JFES; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'employment_onet_q2': {
        'type': 'ONETCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'employment_onet_q4': {
        'type': 'ONETCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'employment_related_to_training_2q_after_exit': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Career ConneCT',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'employment_start_date': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'CYEP; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project; OWS Basic Skills Remediation; Good Jobs',
        'grouped_col_name': 'employment_start',
        'program_count': 7,
    },
    'employment_status_2q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_status_3q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_status_4q_after_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'employment_status_after_exit_q1': {
        'type': 'categorical',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': EMPLOYMENT_STATUS_MAPPING
    },
    'employment_status_at_exit': {
        'type': 'categorical',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Good Jobs; WIOA Adult, WIOA Dislocated Worker, JFES; H1B CT-WHISP; OWS Basic Skills Remediation; Manufacturing Pipeline',
        'grouped_col_name': 'employment_exit',
        'program_count': 6,
        'accepted_responses': EMPLOYMENT_STATUS_MAPPING
    },
    'employment_status_at_start': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Manufacturing Pipeline; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'employment_status_start',
        'program_count': 15,
    },
    'employment_town': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'end_date_funding': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'end_reason': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'end_reason_for_funding_history': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'end_reason',
        'program_count': 11,
    },
    'end_reason_for_training_record': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'end_reason',
        'program_count': 10,
    },
    'english_language_learner': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; CYEP; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 14,
    },
    'enrolled_in_training_program': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'HFPG, UW',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'enrollment_grade_level': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'enrollment_gross_annual_income': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant',
        'grouped_col_name': '',
        'program_count': 8,
    },
    'enrollment_start_date': {
        'type': 'dateTime',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'entered_non_traditional_employment': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'entered_training_related_employment': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'entrepreneurship': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'estimated_financial_aid': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': 'services',
        'program_count': 4,
    },
    'ethnicity': {
        'type': 'categorical',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 51,
        'accepted_responses': ETHNICITY_MAPPING
    },
    'experience_carpentry': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_drafting': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_electrical': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_enginerepair': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_excel': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_generalrepairs': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_machining': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_painting': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_pipefitting': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_planning': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_plastics': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_rigging': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_sheetmetal': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_sheetmetal_plastics': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_shipfitting': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'experience_welding': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'final_scholarship_amount': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'financial_literacy': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'grouped_col_name': 'services',
        'program_count': 3,
    },
    'financial_support': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'first_job': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'first_language_english': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'First Name': {
        'type': 'identifier',
        'Section': 'Unmatched; Section A - Individual Information',
        'programs': 'Manufacturing Pipeline; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 51,
    },
    'food': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'food_and_nutrition': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'foster_care': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': 'supports',
        'program_count': 2,
    },
    'funding_source': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'funding_start_date?': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'gender': {
        'type': 'categorical',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline; CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 52,
        'accepted_responses': GENDER_MAPPING
    },
    'graduating_senior': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'graduation_year': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'green_job': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'gross_annual_income': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information; Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'hartford_promise_zone': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'have_you_been_impacted_by_covid_19?': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'head_of_household': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'healthcare': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'high_passed': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'high_school_diploma': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'high_school_dropout': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; CYEP',
        'grouped_col_name': 'barriers',
        'program_count': 8,
    },
    'highest_education_level_completed_at_program_entry': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP; Manufacturing Pipeline; Congressional Direct Spending/Community Project; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': 'education_entry',
        'program_count': 16,
    },
    'homeless_at_risk': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'homeless_or_runaway': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; CYEP; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 14,
    },
    'hourly_wage_at_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'hourly_wage_at_worksite': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'hours_wk_2': {
        'type': 'hoursWorked',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'household_size': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'housing': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP; HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'how_long_work_construction_and_what_did_you_do': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'hps_credit_recovery_cohort': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'incentive_amount': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP, Bloomfield',
        'grouped_col_name': 'incentive_amount',
        'program_count': 2,
    },
    'incentive_form': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP, Bloomfield',
        'grouped_col_name': 'incentive',
        'program_count': 2,
    },
    'incumbent_worker_advanced_to_new_position_1q_after_completion': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'incumbent_worker_advanced_to_new_position_2q_after_completion': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'incumbent_worker_advanced_to_new_position_3q_after_completion': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'incumbent_worker_retained_position': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'incumbent_worker_retained_position_1q_after_completion': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'incumbent_worker_training': {
        'type': 'categorical',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 2,
        'accepted_responses': INCUMBENT_WORKER_MAPPING
    },
    'initial_scholarship_amount': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'interested_in_employment_search_support': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'interested_working_outside': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'interested_working_with_computers': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'interested_working_with_dress_code_in_professional_setting': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'jfes': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; H1B CT-WHISP; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'job_readiness': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'job_shadowing': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'job_title': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; CYEP; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth',
        'grouped_col_name': '',
        'program_count': 43,
    },
    'job_title_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'justice_involved': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'barriers',
        'program_count': 12,
    },
    'last_date_of_employment': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'Last Name': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; State Youth Employment Programs (OYE, DCF, DADS); Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 51,
    },
    'leadership_development': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'legal_aid': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'legally_allowed_to_work_in_us': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 8,
    },
    'level_up_referral': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'long_term_unemployed_at_program_entry': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'longest_employed_with_one_employer': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'low_income': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 13,
    },
    'lunch_status': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 2,
    },
    'manufacturing_experience': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'marital_status': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'mental_health': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'mentoring': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'middle_name': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 14,
    },
    'migrant_and_seasonal_farmworker': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'monitoring_status': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'most_recent_date_basic_career_services': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': '0',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'most_recent_date_follow_up_service': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'most_recent_date_supportive_services': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'most_recent_job_days_employed': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'most_recent_job',
        'program_count': 11,
    },
    'most_recent_job_hourly_wage': {
        'type': 'hourlyWage',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': 'most_recent_job',
        'program_count': 4,
    },
    'most_recent_job_hours_worked': {
        'type': 'hoursWorked',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': 'most_recent_job',
        'program_count': 4,
    },
    'most_recent_job_industry': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': 'most_recent_job',
        'program_count': 4,
    },
    'most_recent_job_last_date_of_employment': {
        'type': 'dateTime',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'most_recent_job',
        'program_count': 6,
    },
    'most_recent_job_onet': {
        'type': 'ONETCode',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'most_recent_job',
        'program_count': 4,
    },
    'most_recent_job_title': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': 'most_recent_job',
        'program_count': 4,
    },
    'most_recent_sye_participation': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'naics': {
        'type': 'NAICSCode',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'national_dislocated_workers_grant': {
        'type': 'categorical',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': DISLOCATED_WORKER_MAPPING
    },
    'occupational_skills_training': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'onet_training_1': {
        'type': 'ONETCode',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; Good Jobs; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 12,
    },
    'onet_training_2': {
        'type': 'ONETCode',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'onet_training_3': {
        'type': 'ONETCode',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'organization': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'orientation_s_or_ns': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'other_barriers_1': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': 'barriers',
        'program_count': 2,
    },
    'other_barriers_2': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'other_public_assistance_recipient': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'supports',
        'program_count': 1,
    },
    'other_reasons_for_exit': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'other_supportive_services': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'other_work/trade_certifications': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'paid_competency_training_hours': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'paid_worksite_hours': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'parent_or_pregnant': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; CYEP; Congressional Direct Spending/Community Project; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': 'barriers',
        'program_count': 15,
    },
    'past_participant_in_cyep': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'pathways': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'permit_or_driver_license': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'placement_made_through_program': {
        'type': 'boolean',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'portal_application_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'post_secondary_transition_activities': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'pre_apprenticeship': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'primary_funding': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'primary_funding_other': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'primary_training_funding': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'primary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'primary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'primary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'program_operator': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'provider': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'race/ethnicity': {
        'type': 'categorical',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline; Congressional Direct Spending/Community Project; CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': 'race/ethnicity',
        'program_count': 52,
        'accepted_responses': RACE_ETHNICITY_MAPPING
    },
    'rapid_response': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'rapid_response_additional_assistance': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'received_needs_related_payments': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'received_training': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; Good Jobs; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 36,
    },
    'receiving_dcf_or_foster_care_services': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'supports',
        'program_count': 13,
    },
    'referral_source': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'registered_apprenticeship': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'registered_selective_service': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'registration_submission_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'reliable_transportation': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'resume': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'retention_with_same_employer_2q_and_4q': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'saga': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'supports',
        'program_count': 2,
    },
    'sasid': {
        'type': 'identifier',
        'Section': 'Section A - INDIVIDUAL INFORMATION',
        'programs': 'CYEP; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'scheduled_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways; Good Jobs; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'scheduled_start_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 7,
    },
    'school_status_at_exit': {
        'type': 'identifier',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Career ConneCT; Good Jobs; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'school_status_at_program_entry': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; State Youth Employment Programs (OYE, DCF, DADS); HFPG, UW; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 16,
    },
    'secondary_funding': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'secondary_funding_other': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'secondary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'secondary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'secondary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'sector': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'selective_service': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP; State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'servsafe_certified': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'single_parent': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Good Jobs; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 3,
    },
    'snap': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; State Youth Employment Programs (OYE, DCF, DADS); OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; WIOA Youth Pathways; WIOA Adult, WIOA Dislocated Worker, JFES; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'supports',
        'program_count': 15,
    },
    'snap_tanf_saga': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': 'supports',
        'program_count': 1,
    },
    'special_requirement': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'ssi/ssdi': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant',
        'grouped_col_name': 'supports',
        'program_count': 8,
    },
    'ssi_ssdi': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Career ConneCT; Good Jobs; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'supports',
        'program_count': 3,
    },
    'ssn': {
        'type': 'identifier',
        'Section': 'Unmatched; Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project; CYEP; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 16,
    },
    'state': {
        'type': 'stateID7',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP; Manufacturing Pipeline; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'substance_use': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'suffix': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'summer_program_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'summer_program_start_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'support_type': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'services',
        'program_count': 11,
    },
    'support_value': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'services_amount',
        'program_count': 11,
    },
    'supports_other': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': 'services',
        'program_count': 1,
    },
    'supports_provided_1': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': 'supports',
        'program_count': 1,
    },
    'supports_provided_2': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'CYEP',
        'grouped_col_name': 'supports',
        'program_count': 1,
    },
    'tanf': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS); OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; Congressional Direct Spending/Community Project',
        'grouped_col_name': 'supports',
        'program_count': 10,
    },
    'tertiary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'tertiary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'tertiary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'test_score': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'third_funding': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'third_funding_other': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'ticket_to_work': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs',
        'grouped_col_name': 'supports',
        'program_count': 3,
    },
    'total_program_costs': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'town_person': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Manufacturing Pipeline; CYEP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; Good Jobs; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth; OWS Basic Skills Remediation; Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; H1B Nursing Expansion Grant; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; HFPG, UW; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 53,
    },
    'training_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways; Good Jobs; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 11,
    },
    'training_1_area': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; HFPG, UW; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'training_1_category': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'training_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'training_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'training_completed_1': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; WIOA Adult, WIOA Dislocated Worker, JFES; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 41,
    },
    'training_completed_2': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'training_completed_3': {
        'type': 'boolean',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'training_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; CYEP; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 13,
    },
    'training_format': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; Good Jobs; H1B CT-WHISP; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; WIOA Youth Pathways; CYEP, Bloomfield; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': '',
        'program_count': 10,
    },
    'training_job_title': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; CYEP',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'training_program_id': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Adult, WIOA Dislocated Worker, JFES; Career ConneCT; H1B CT-WHISP; WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'training_provider': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Good Jobs; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield; WIOA Adult, WIOA Dislocated Worker, JFES; H1B CT-WHISP; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; OWS Basic Skills Remediation; H1B Nursing Expansion Grant; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; HFPG, UW; WIOA Youth Recruitment',
        'grouped_col_name': '',
        'program_count': 14,
    },
    'training_wages': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'training_weekly_hours': {
        'type': 'hoursWorked',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; CYEP',
        'grouped_col_name': '',
        'program_count': 3,
    },
    'transportation': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP; HFPG, UW',
        'grouped_col_name': 'services',
        'program_count': 2,
    },
    'type_of_crime': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'barriers',
        'program_count': 2,
    },
    'type_service': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; Good Jobs; IREE; P2E Reentry; Pathway HOME; P2E; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; CYEP; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; P2E Youth',
        'grouped_col_name': 'services',
        'program_count': 37,
    },
    'type_training_1': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; NEXP; HRSA CHWT; CCCT Healthcare; Bpt ARPA CHW; Mortgage Crisis; Mortgage Crisis ARPA; Project Retail; Good Jobs; ACI Manufacturing; ACI Healthcare; ACJ WIOA; BRBC; CCCT CDL; CCCT Green Jobs; CCCT; CCCT Remote Works; DOL Energy Works; JFES; New Youth Build; Project RISE; WHISP; YARG; Manufacturing; ARPA Youth; BBF ARPA; BBF CT; BRS; CSSD; DCF; ODEP/ETM; WIOA Youth; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 36,
    },
    'type_training_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'type_training_3': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Career ConneCT; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'underemployed': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 5,
    },
    'unemployment_compensation': {
        'type': 'categorical',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project; OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed',
        'grouped_col_name': 'supports',
        'program_count': 7,
        'accepted_responses': UC_MAPPING
    },
    'veteran_status': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; HFPG, UW; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; Good Jobs; H1B CT-WHISP; H1B Nursing Expansion Grant; WIOA Adult, WIOA Dislocated Worker, JFES; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG; CYEP, Bloomfield; Manufacturing Pipeline; Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 14,
    },
    'wage_hr_2': {
        'type': 'hourlyWage',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_1q_after_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_1q_prior': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_2q_after_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_2q_prior': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_3q_after_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_3q_prior': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_4q_after_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'wages_after_exit': {
        'type': 'hourlyWage',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'CYEP; Manufacturing Pipeline',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'wagner_peyser_employment_service': {
        'type': 'categorical',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': WAGNER_PEYSER_MAPPING
    },
    'week_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield',
        'grouped_col_name': '',
        'program_count': 2,
    },
    'week_ending_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'which_services_would_be_helpful': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; H1B CT-WHISP',
        'grouped_col_name': '',
        'program_count': 4,
    },
    'wioa_id': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'work_site': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'work_site_town': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'work_supports': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'workforce_board_code': {
        'type': 'identifier',
        'Section': 'Section A - Individual Information',
        'programs': 'Career ConneCT',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'worksite_2': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'worksite_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'worksite_total_hours': {
        'type': 'hoursWorked',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'WIOA Youth Pathways',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'worksite_town': {
        'type': 'identifier',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'year_of_graduation': {
        'type': 'identifier',
        'Section': 'Unmatched',
        'programs': 'CYEP',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'year_round_program_end_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'year_round_program_start_date': {
        'type': 'dateTime',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'grouped_col_name': '',
        'program_count': 1,
    },
    'youth_needs_additional_assistance': {
        'type': 'boolean',
        'Section': 'Section A - Individual Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': 'barriers',
        'program_count': 1,
    },
    'youth_placement_2q': {
        'type': 'categorical',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': YOUTH_PLACEMENT_MAPPING
    },
    'youth_placement_4q': {
        'type': 'categorical',
        'Section': 'Section D - Program Outcomes Information',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': YOUTH_PLACEMENT_MAPPING
    },
    'youth_services': {
        'type': 'categorical',
        'Section': 'Section C - One Stop Services and Activities',
        'programs': 'Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 1,
        'accepted_responses': YOUTH_SERVICES_MAPPING
    },
    'zip_code': {
        'type': 'zipCode',
        'Section': 'Section A - Individual Information',
        'programs': 'OWS Basic Skills Remediation; Career ConneCT; Good Jobs; Best Chance, Jobs Funnel, WE RISE, CDS; O2i, Free to Succeed; WIOA Adult, WIOA Dislocated Worker, JFES; H1B CT-WHISP; HFPG, UW; H1B Nursing Expansion Grant; WIOA Youth Recruitment; WIOA Youth Pathways; CYEP, DCF, CSSD, ADS, City of Hartford, HFPG; CYEP, Bloomfield; CYEP; Manufacturing Pipeline; State Youth Employment Programs (OYE, DCF, DADS); Congressional Direct Spending/Community Project',
        'grouped_col_name': '',
        'program_count': 17,
    }
}  

# Workbook definitions
workbook_definitions = {

    "pa25_119 data":{
        "simple format": {
        
            "Report":{
            "labels": simple_format_pa25_119_data_labels,
            "accepted_responses": simple_format_pa25_119_data_accepted_responses_w_types,
            "s_used": None,
            "starting_row": 0,
            "sheet_name": "Report",
            "starting_": 0 # zero covers whole df
            }
        }
    }
}