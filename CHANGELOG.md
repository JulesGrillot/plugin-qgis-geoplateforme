# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.10.0 - 2022-09-01

- tile creation: display zoom level in labels (see #34 and !101)
- tile creation: round scale for zoom level informations (see #34 and !101)
- settings update and improvments (see !103):
  - set production URLs as defaults
  - add URL for appendices API
  - add reset to default button and logic

## 0.9.0 - 2022-08-29

- Update stored dataset
- View output tiles service into QGIS
- Add ability to unpublish a service
- Add ability to delete data
- Display available uploads into dashboard
- Add sample generation
- Display dataset extent
- Improve processing waith & run
- Improve CRS picker into update form
- Improve tippecanoe options UI
- Add Sonar Cloud analisis
- Minor improvments on settings management
- Various bug fixes

## 0.8.0 - 2022-08-12

- Report dialog for stored data  - !65 !68 !69 !84 / #65
- Add refresh / create / update actions to dashboard - !82 !83 / #55 #59
- Add method to copy label to clipboard - !66 / #78
- Storage data report - !70 / #9
- ui refactor - !73
- display date in dashboard - !76
- add view action to display vector tile in QGIS !80
- unpublish tiles - !78 / #63 #64
- fix removal of current connection when disconnecting - !77
- limit file type used for upload - !74 / #90
- fix layers checked before upload - !75
- don't add tippecanoe option in tile creation parameters if not defined - !72 / #84
- fix attributes list definition - !81 / #93

## 0.7.0 - 2022-08-04

- Add first version of Dashboard - !37
- Feature/get endpoint - !54
- Refactoring translation - !59
- Add zoom levels parameters - !55
- Improve displayed datetime using localization - !60
- Move plugin to web menu and add actions - !61
- Fix URL regex - !57
- Minor bug fixes

## 0.6.0 - 2022-07-27

- Add configuration and offering processing and .ui for publication
- refactoring of Authentication dialog
- refactoring of text validators
- end of sprint 3 (the second of active development)

## 0.5.1 - 2022-07-07

- Change client id from `guichet` to `geotuileur-qgis-plugin` to fix #81
- plugin has been renamed from `Vectiler` to `Geotuileur` (alternatively `Géotuileur`)
- plugin's metadata are complete

## 0.5.0 - 2022-06-30

- Switch to .json for processing parameters : See #72 #76 #73
- Improve features attributes picking : See #52
- Add user account UI :#56
- Add data integration check : See #51
- Minor bug fixes : See #48 #33 #28 #27

## 0.4.0 - 2022-06-23

- Improve feature attributes selection widget. See: #52 - !30 (sorting in !34)
- Improve connection widget behavior. See: #28 - !28
- Fix wizard refresh. See: !33
- Fix proxy handling for upload operations. See: #50 - !32
- Fix bad interpretation of Tippecanoe options. See: #27 - !27

## 0.3.0 - 2022-06-21

- Complete authentication workflow using QGIS Authentication Manager and proper oAuth2 grant flow
- Add processing to prepare dataset
- Add processing to upload dataset
- Add UI elements for main thre steps: authentication, dataset upload, storage listing and vector tile processing
- Use Geotuileur icons
- Partial translation into French

## 0.2.1 - 2022-06-01

- Fix CI build

## 0.2.0 - 2022-06-01

- Add connection settings
- Add a minimal API client to test authentication flow
- Minor fixes

## 0.1.0 - 2022-05-11

- First release
- Generated with the [QGIS Plugins templater](https://oslandia.gitlab.io/qgis/template-qgis-plugin/)
