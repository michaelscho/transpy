# export
export_folder="/path/to/folder/"

resources_folder = "/path/to/folder/"

exist_url = "url/to/existdb/"

special_characters_dict = {'-ur':'\uf1c2',
        '-bus':'\uf1ac',
        'b mit Strich':'\u0180',
        'd mit Strich':'\u0111',
        'h mit Strich':'\u0127',
        'K mit Strich':'\uA740',
        'k mit Strich':'\uA741',
        'L mit hohem Strich':'\uA748',
        'l mit hohem Strich':'\uA749',
        'l mit mittlerem Strich':'\u019A',
        'Pre':'P\u0304',
        'pre':'p\u0304',
        'Per':'\uA750',
        'per':'\uA751',
        'Pro':'\uA752',
        'pro':'\uA753',
        'Nasalstrich':'\u0304',
        'Kürzungsstrich':'\u0305',
        'q mit Strich':'\uA757',
        'q mit Schlaufe':'\uA759',
        '-rum':'\ua75D',
        '-RUM':'\ua75C',
        '-us':'\u1DD2',
        '-a (hochgestellt)':'\u1DD3',
        '-i (hochgestellt)':'\u0365',
        'hochgestelltes -o':'\u0366',
        'hochgestelltes -u':'\u0367',
        'Antwort-Zeichen R':'\u211E',
        'Q mit Strich':'\uA756',
        'Q mit Schlaufe':'\uA758'}

rules_for_expansion = {'om̅': 'omn',
    '\uf1c2': 'ur',
    'P\u0304': 'Prae',
    'p\u0304': 'prae',
    '\uA750': 'Per',
    '\uA751': 'per',
    '\uA752': 'Pro',
    '\uA753': 'pro',
    '\u0304': 'm',
    '\ua75D': 'rum',
    '\ua75C': 'RUM',
    'q\uf1ac': 'que',
    'Q\u0366': 'Quo',
    'q\u0366': 'quo',
    'q\u1dd3': 'qua',
    'Q\u1dd3': 'Qua',
    'q\u0365': 'qui',
    'p\u0365': 'pri',
    'Q\u0365': 'Qui',
    'b\uf1ac': 'bus',
    '\u1DD2': 'us',
    'c\u0305': 'con',
    'C\u0305': 'Con',
    'm\u0305': 'men',
    't̅': 'ter',
    'r̅': 'runt'}

character_list = [['<g ref="#char-f1ac"></g>',''],
    ['<pc type="distinctio"><g ref="#char-f1f8"></g></pc>',''],
    ['<pc type="p-versus"><g ref="#char-f1ea"></g></pc>',''],
    ['<pc type="p-flexus"><g ref="#char-f1f5"></g></pc>',''],
    ['<pc type="p-comma-positura"><g ref="#char-f1e4"></g></pc>',''],
    ['<pc type="p-elevatus"><g ref="#char-f1f0"></g></pc>',''],
    ['<pc type="p-interrogativus"><g ref="#char-f160"></g></pc>',''],
    ['<pc type="p-interrogativus-positura"><g ref="#char-int-posit"></g></pc>',''],
    ['<g ref="#char-f1e1"></g>',''],
    ['<g ref="#char-0180">ƀ</g>','ƀ'],
    ['<g ref="#char-0111">đ</g>','đ'],
    ['<g ref="#char-0127">ħ</g>','ħ'],
    ['<g ref="#char-f1c2"></g>',''],
    ['<g ref="#char-a740">Ꝁ</g>','Ꝁ'],
    ['<g ref="#char-a741">ꝁ</g>','ꝁ'],
    ['<g ref="#char-a748">Ꝉ</g>','Ꝉ'],
    ['<g ref="#char-a749">ꝉ</g>','ꝉ'],
    ['<g ref="#char-019a">ƚ</g>','ƚ'],
    ['<g ref="#char-0118">Ę</g>','Ę'],
    ['<g ref="#char-0119">ę</g>','ę'],
    ['<g ref="#char-a750">Ꝑ</g>','Ꝑ'],
    ['<g ref="#char-a751">ꝑ</g>','ꝑ'],
    ['<g ref="#char-a752">Ꝓ</g>','Ꝓ'],
    ['<g ref="#char-a753">ꝓ</g>','ꝓ'],
    ['<g ref="#char-0304">&#x0304;</g>','\u0304'],
    ['<g ref="#char-0305">&#x0305;</g>','\u0305'],
    ['<g ref="#char-a757">ꝗ</g>','ꝗ'],
    ['<g ref="#char-a759">ꝙ</g>','ꝙ'],
    ['<g ref="#char-a75D">ꝝ</g>','ꝝ'],
    ['<g ref="#char-a75C">Ꝝ</g>','Ꝝ'],
    ['<g ref="#char-1dd2">&#x1dd2;</g>','\u1dd2'],
    ['<g ref="#char-1dd3">&#x1dd3;</g>','\u1dd3'],
    ['<g ref="#char-0365">&#x0365;</g>','\u0365'],
    ['<g ref="#char-0300">◌̀</g>','◌̀'],
    ['<g ref="#char-0301">◌́</g>','◌́'],
    ['<g ref="#char-0302">◌̂</g>','◌̂'],
    ['<g ref="#char-0306">◌̆</g>','◌̆'],
    ['<g ref="#char-0366">◌ͦ</g>','◌ͦ'],
    ['<g ref="#char-0367">◌ͧ</g>','◌ͧ'],
    ['<g ref="#char-211E">℞</g>','℞'],
    ['<g ref="#char-a756">Ꝗ</g>','Ꝗ'],
    ['<g ref="#char-a758">Ꝙ</g>','Ꝙ'],
    ['<g ref="#char-2234">∴</g>','∴'],
    ['<g ref="#char-23D1">⏑</g>','⏑']]

manuscript_data = { 'F': {
                        'signatur': 'Frankfurt a.M., UB, Barth. 50',
                        'transkribus_collection_id': 80437,
                        'transkribus_document_id': 637541,
                        'base_folder': '01_Transkription_Frankfurt-ub-b-50',
                        'tei_base_id': 'frankfurt-ub-b-50-',
                        'iiif_scale_factor': 1.34,
                        'facs_url':'f"https://sammlungen.ub.uni-frankfurt.de/i3f/v20/{self.iiif_image_id}/full/full/0/default.jpg"',
                        'corresp':'f"https://sammlungen.ub.uni-frankfurt.de/msma/i3f/v20/2035614/canvas/{self.iiif_image_id}"',
                        'ana':'f"/annotations/frankfurt-ub-b-50-annotation-{self.iiif_image_id}"'},

                    'B': {
                        'signatur': 'Bamberg, SB, Can. 6',
                        'transkribus_collection_id': 80437,
                        'transkribus_document_id': 732612,
                        'base_folder': '01_Transkription_Bamberg_Stabi_Can_6',
                        'tei_base_id': 'bamberg-sb-c-6-',
                        'iiif_scale_factor': 1,
                        'facs_url':'f"https://api.digitale-sammlungen.de/iiif/image/v2/bsb00140701_00{self.iiif_image_id}/full/full/0/default.jpg"',
                        'corresp':'f"https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00140701/canvas/{self.iiif_image_id}"',
                        'ana':'f"/annotations/bamberg-sb-c-6-annotation-{self.iiif_image_id}"'},

                    'K': {
                        'signatur': 'Köln, EDD, Cod. 119',
                        'transkribus_collection_id': 80437,
                        'transkribus_document_id': 796594,
                        'base_folder': '01_Transkription_Köln_EDD_Cod_119',
                        'tei_base_id': 'koeln-edd-c-119-',
                        'iiif_scale_factor': 1,
                        'facs_url':'f"https://digital.dombibliothek-koeln.de/i3f/v20/{self.iiif_image_id}/full/full/0/default.jpg"',
                        'corresp':'f"https://digital.dombibliothek-koeln.de/i3f/v20/284343/canvas/{self.iiif_image_id}"',
                        'ana':'f"/annotations/koeln-edd-c-119-annotation-{self.iiif_image_id}"'},

                    'Va': {
                        'signatur': 'Vatikan, BAV, Pal. lat. 585',
                        'transkribus_collection_id': 80437,
                        'transkribus_document_id': 855714,
                        'base_folder': '01_Transkription_BAV_Pal_lat_585',
                        'tei_base_id': 'vatican-bav-pal-lat-585-',
                        'iiif_scale_factor': 1,
                        'facs_url':'f"https://digi.vatlib.it/pub/digit/MSS_Pal.lat.585/iiif/Pal.lat.585_{str(self.iiif_image_id).zfill(4)}_fa_{self.start_folio[:-1].zfill(4)+self.start_folio[-1:]}.jp2/full/full/0/default.jpg"',
                        'corresp':'f"https://digi.vatlib.it/iiif/MSS_Pal.lat.585/canvas/p{str(self.iiif_image_id).zfill(4)}"',
                        'ana':'f"/annotations/vatican-bav-pal-lat-585-annotation-p{str(self.iiif_image_id).zfill(4)}"'},

                    'Vb': {
                        'signatur': 'Vatikan, BAV, Pal. lat. 586',
                        'transkribus_collection_id': 80437,
                        'transkribus_document_id': 1197208,
                        'base_folder': '01_Transkription_BAV_Pal_lat_586',
                        'tei_base_id': 'vatican-bav-pal-lat-586-',
                        'iiif_scale_factor': 1,
                        'facs_url':'f"https://digi.vatlib.it/pub/digit/MSS_Pal.lat.585/iiif/Pal.lat.586_{str(self.iiif_image_id).zfill(4)}_fa_{self.start_folio[:-1].zfill(4)+self.start_folio[-1:]}.jp2/full/full/0/default.jpg"',
                        'corresp':'f"https://digi.vatlib.it/iiif/MSS_Pal.lat.586/canvas/p{str(self.iiif_image_id).zfill(4)}"',
                        'ana':'f"/annotations/vatican-bav-pal-lat-586-annotation-p{str(self.iiif_image_id).zfill(4)}"'},
}