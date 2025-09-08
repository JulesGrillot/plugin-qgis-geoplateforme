# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.14.0 - 2025-09-08

### Bugs fixes 🐛

* fix(processing): be more robust for processing search from id by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/237>
* fix(qt6): remove use of child function (replaced by index) by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/238>
* fix(markdown): in Qt6 standard markdown is used, italic which _ is not supported by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/240>
* fix(report): avoid duplicate of generation report by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/239>
* fix(doc): invalid links for processings by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/247>
* Fix/update user key accesses by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/250>
* feat(wfs): use QScrollArea to use collapsible group box by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/253>
* fix(offering model): use /datastore/{datastore]/offerings to get list of offering if no dataset defined by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/261>
* fix(dashboard): dataset not selected after creation and set upload wizard min height by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/265>

### Features and enhancements 🎉

* feat(ui): add check for pyr vector and pyr raster generation parameters by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/251>
* feat(pyr_vector): remove sample option by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/252>
* feat(metadata): edit metadata description with markdown by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/254>
* feat(publish): enable back button in case of publish error by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/255>
* Feat/init translation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/259>
* feat(dashboard): run metadata update in QgsTask by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/263>
* feat(dashboard): disable widget during refresh and update model in a QgsTask by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/264>

### Tooling 🔧

* build(deps): bump actions/checkout from 4 to 5 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/258>
* build(deps): bump dawidd6/action-download-artifact from 9 to 10 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/96>
* build(deps): bump actions/upload-pages-artifact from 3 to 4 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/257>
* build(deps): bump actions/download-artifact from 4 to 5 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/256>
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/154>
* build(deps-dev): update ruff requirement from <0.12.0,>=0.11.5 to >=0.11.5,<0.13.0 in /requirements by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/150>

### Documentation 📖

* Doc/init doc for widget by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/260>

## New Contributors

* @dependabot[bot] made their first contribution in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/258>
* @pre-commit-ci[bot] made their first contribution in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/154>

## 0.13.0 - 2025-08-22

### Bugs fixes 🐛

* fix(qt6): update enum use for qt6 compatibility by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/211>
* fix(provider): display result info when selection is changed by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/215>
* feat(processing): always use ids instead of names by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/217>
* feat(sld from layer): disable checks to avoid error if proxy needed for schema download by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/219>

### Features and enhancements 🎉

* feat(offering): allow delete of UNSTABLE offerings by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/212>
* feat(wfs): add validator for public name by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/213>
* feat(theme): sort theme by value for display by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/216>
* feat(dashboard): update min size by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/218>

## 0.12.0 - 2025-08-13

### Bugs fixes 🐛

* fix(search): add tag widget for theme field and fix production year search by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/185>
* fix(permission): invalid groupId for create_permission by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/187>
* fix(user key): login and password are mandatory for BASIC key by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/188>
* fix(publish): first page is not a commit page, metadata page is by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/189>
* fix(wms): invalid parameter datastore for geoserver style creation must use datastore_id by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/192>
* fix(stored data): need to check enum not string for status text by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/193>
* feat(dashboard): avoid multiple refresh when multiple display ask by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/194>
* fix(actions): use layout instead of toolbar for actions by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/195>
* fix(stored data): allow delete if status is UNSTABLE by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/197>
* fix(provider): use user define authid for authentication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/199>

### Features and enhancements 🎉

* feat(sld transform): add transform to lowercase for ogc:PropertyName by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/190>
* feat(markdown): add editor for configuration abstract by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/191>
* feat(sld): add option to create sld file from layer by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/196>
* feat(publish): add page to define publication visibility by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/198>
* feat(metadata): publish metadata on METADATA endpoint after creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/200>
* feat(metadata): unpublish if no service available for dataset by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/201>
* feat(dashboard): add button to delete current dataset by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/202>
* feat(metadata): metadata create/update and publish are done in task by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/203>
* update(index): tagging and update configurations with metadata by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/186>
* Update metadata.txt by @IGNF-Xavier in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/184>

## 0.11.0 - 2025-08-01

### Features and enhancements 🎉

* feat(metadata): Update metadata links (access, styles and getCapabilities) by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/166>
* feat(metadata): Add better UI for metadata and combo lists by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/174>
* feat(search-provider): add auth selector and new UI for advanced search by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/177>

## 0.10.0 - 2025-07-23

### Bugs fixes 🐛

* fix(style): None return for configuration.extra if no styles available by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/159>
* fix(pyr raster): offering now contains Configuration object and not dict by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/160>
* fix(publication): no need for zoom level definition for WMS Raster and WMS-TMS by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/162>
* fix(unpublish): wait for offering unpublication and check if configuration must be deleted by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/164>

### Features and enhancements 🎉

* Add processing and metadata form in tiles publication interface by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/155>
* Ajout du formulaire de métadonnée pour les publication wms et wmts by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/156>
* feat(style): update configuration metadata and synchronize offering after style add/delete by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/161>
* Load service from dashboard by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/163>

## 0.9.0 - 2025-07-03

### Features and enhancements 🎉

* feat(annexe): add processing for annexe creation and delete by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/147>
* feat(style): new processing to add style to service configuration by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/148>
* feat(style): display configuration style for a service by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/149>
* feat(user key): ask user for QGIS auth creation after user key creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/152>

## 0.8.0 - 2025-06-23

### Bugs fixes 🐛

* fix(dataprovider): remove provider from sourceSelectProviderRegistry at unload by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/130>
* fix(processing): add output to be able to use processing in QGIS modeler by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/144>

### Features and enhancements 🎉

* feat(upload): add processing and GUI for upload delete by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/120>
* feat(unpublish): add processing for offering delete by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/121>
* feat(user key): display available keys in table by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/122>
* feat(permission): add processing for permission creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/123>
* feat(permission): add widget to display permission in closed services by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/124>
* feat(permission): add permission creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/126>
* Feat/new metadata widget by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/125>
* feat(user key): add processing for key creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/127>
* feat(user key): add accesses creation processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/128>
* feat(user key): add dialog to create user key by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/129>
* refactor(processing): remove unused processing and dead code by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/131>
* feat(user key): display user key by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/132>
* feat(user key): add button to delete key by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/133>
* feat(user key): add button to delete selected ip by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/135>
* feat(user key): add specific component for IP CIDR adress edit by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/136>
* feat(user key): display only permission with end date over now by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/137>
* feat(user key): check that at least one offering is selected by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/138>
* feat(user key): add processing and GUI for update  by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/140>
* feat(permission): add widget to display / delete / update permission by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/141>
* feat(dashboard): move button and add permission widget by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/142>
* feat(permission): display public community for creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/143>
* feat(permission): small fixes and add option to delete added user and community by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/145>

## 0.7.0 - 2025-06-04

### Bugs fixes 🐛

* fix(endpoint): add option to use open endpoint by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/95>

### Features and enhancements 🎉

* Feature/add provider gpf by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/106>
* feat(delete): add delete action for stored data by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/105>
* feat(delete): add processing to delete stored data and associated offering and configuration by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/104>
* feat(procesing): move processing to a dedicated dir for each group by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/103>
* Feat/update documentation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/102>
* feat(wmts): add wizard for publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/101>
* feat(wmts): init processing for publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/100>
* feat(wms raster): add wizard for publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/99>
* feat(wms raster): init processing for publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/98>
* feat(raster tiles): add wizard for raster tiles creation from WMS-VECTOR service by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/97>

## 0.6.0 - 2025-05-28

### Bugs fixes 🐛

* fix(network manager): don't push log in message bar to avoid crashes in Windows by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/71>
* fix(upload): set datasetname in tags by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/72>
* Fix/no crs if no layer from qgis by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/74>
* fix(upload): always use temporary file for gpkg layers to avoid upload of other layers by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/75>
* fix(dataset): show dataset with only upload by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/78>
* fix(upload): add_file need a Path and not a str by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/89>
* fix(tms): need to use ConfigurationType instead of str by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/91>
* fix(offering): always publish as open by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/93>

### Features and enhancements 🎉

* Feat/init style file creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/61>
* Feat/minimal sld downgrade by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/62>
* feat(upload): refactor wizard to check for upload close before database integration by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/77>
* feat(vector db): add generation wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/79>
* feat(tms): select stored data after generation launch by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/80>
* feat(tile): wait option in tile generation processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/81>
* feat(upload): add tag for upload integration steps by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/82>
* feat(ui): move to plugin menu and add report button by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/88>
* feat(wms vector): init processing for publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/83>
* feat(wms vector): init publication wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/84>
* feat(service): display offering instead of configuration by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/85>
* feat(service): add details zone by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/86>
* feat(upload): select upload or stored data after creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/90>
* feat(publication): select offering after publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/92>

## 0.5.0 - 2025-05-22

### Features and enhancements 🎉

* Feat/init wfs publication by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/54>
* Feat/wfs publication wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/55>

### Bugs fixes 🐛

* fix(metadata): use temporary file name only but not with context by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/58>

## 0.4.0 - 2025-05-21

* Feat/remove check of crs for non spatial layers by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/34>
* feat(upload): add processing for creation from QGIS layer by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/31>
* feature(dashboard): add button to create a new dataset or add data to existing dataset by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/32>
* feat(tile publish): add prefix SANDBOX for list of datastore defined in settings by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/33>
* 4- feat(upload to vector): refactor to replace .json by processing parameter by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/35>
* 5- feat(upload from layer): add additionnal files option by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/36>
* feat(layer selection): new ui for layer and file selection by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/37>
* feat(vector db creation): use layers for vector db creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/38>
* feat(tile generation): add action for tile generation in vector db stored data details by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/39>
* feat(tile publish): add action for tile publication in pyramid vector stored data details by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/40>
* feat(tile generation): refactor to remove JSON file use by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/41>
* feat(tile publish): refactor to remove JSON file use by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/42>
* feat(ui): remove action for tile generation and publication from toolbar by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/43>
* add metadata class and fill by parsing xml by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/48>
* feat(dataset): sort by name in combobox by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/47>
* feat(service): display available service in table by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/44>
* feat(upload): add widget to display upload details by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/45>
* feat(external plugins): add dependencies and load actions in Geoplateforme plugin by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/46>
* feat(ui): minor changes in UI and processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/49>
* feat(processing): add available processings name in settings (not visible to user) by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/50>
* feat(upload): check if db integration has started before wizard close by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/51>
* feat(auth): add user dialog if log in by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/52>

## 0.3.0-beta1 - 2025-04-29

* first version deployed on plugins.qgis.org
* feat(tile creation): no upload remove after creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/26>
* fix(datastore selection): disable signal connection during update by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/25>
* fix(tile publish): invalid levels used by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/28>
* fix(endpoint): invalid search of endpoint by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/30>
* update(ui): use logo proposed by @IGNF-Xavier by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/27>

## 0.2.0-beta2 - 2025-04-29

* fix(plugin): Qt6 flag is supportsQt6 not qt6_compatible by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/22>
* feature(tile creation): restore tile creation wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/17>
* feature(vector tile publish): restore publication wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/20>
* feat(network manager): get error from request reply by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/21>
* feature(upload) : refactor upload creation by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/23>

## 0.2.0-beta1 - 2025-04-23

* feature(auth): Add OAuth2 authentication by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/2>
* feature(dasboard) : add combobox to filter datastore by dataset  by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/7>
* feature(dashboard): add new UI to fit IGNGPF-4830 by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/8>
* feature(packaging): include oAuth credentials from GH Actions secrets during packaging steps by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/14>
* feature(vector db): restore vector db creation wizard by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/16>
* refactor(network): Nettoyage et refactoring du Network Manager by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/6>
* refactor(stored data): optimize stored data for better load by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/9>
* refactor(upload): refactor upload to optimize and use network manager by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/10>
* fix(auth): make QGIS auth configuration map JSON compliant before loading it as JSON by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/13>
* fix(ci): fix packaged plugin and repository was missing in documentation by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/11>
* fix(init): plg_settings.qgis_auth_id can be None and so have no length by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/12>
* fix(quality): apply Qt6 migration script by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/4>
* fix(user): fix community without user  by @Ducarouge in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/18>
* update(plugin): cleanup, remove and rename from geotuileur to geoplateforme by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/1>
* update(tooling): replace black with ruff formatter by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/3>
* update(tooling): set ruff as Python formatter in VS Code by @Guts in <https://github.com/Geoplateforme/plugin-qgis-geoplateforme/pull/5>

## 0.1.0 - 2025-04-10

* First release
* Generated with the [QGIS Plugins templater](https://oslandia.gitlab.io/qgis/template-qgis-plugin/)
