FORMS = ../../gui/dlg_settings.ui \
    ../../gui/dlg_authentication.ui \
    ../../gui/tile_creation/qwp_tile_generation_edition.ui \
    ../../gui/tile_creation/qwp_tile_generation_fields_selection.ui \
    ../../gui/tile_creation/qwp_tile_generation_generalization.ui \
    ../../gui/tile_creation/qwp_tile_generation_status.ui \
    ../../gui/upload_creation/qwp_upload_creation.ui \
    ../../gui/upload_creation/qwp_upload_edition.ui \
    ../../gui/user/dlg_user.ui \
    ../../gui/user/dlg_user.ui

SOURCES= ../../plugin_main.py \
    # API
    ../../api/check.py \
    ../../api/client.py \
    ../../api/execution.py \
    ../../api/processing.py \
    ../../api/stored_data.py \
    ../../api/upload.py \
    # GUI
    ../../gui/cbx_datastore.py \
    ../../gui/cbx_stored_data.py \
    ../../gui/dlg_authentication.py \
    ../../gui/dlg_settings.py \
    ../../gui/mdl_datastore.py \
    ../../gui/mdl_execution_list.py \
    ../../gui/mdl_stored_data.py \
    ../../gui/proxy_model_stored_data.py \
    ../../gui/tile_creation/qwp_tile_generation_edition.py \
    ../../gui/tile_creation/qwp_tile_generation_fields_selection.py \
    ../../gui/tile_creation/qwp_tile_generation_generalization.py \
    ../../gui/tile_creation/qwp_tile_generation_status.py \
    ../../gui/tile_creation/wzd_tile_creation.py \
    ../../gui/upload_creation/qwp_upload_creation.py \
    ../../gui/upload_creation/qwp_upload_edition.py \
    ../../gui/upload_creation/wzd_upload_creation.py \
    ../../gui/user/dlg_user.py \
    ../../gui/user/wdg_user.py \
    # Processings
    ../../processing/check_layer.py \
    ../../processing/provider.py \
    ../../processing/tile_creation.py \
    ../../processing/upload_creation.py \
    ../../processing/upload_database_integration.py \
    # Toolbelt
    ../../toolbelt/log_handler.py \
    ../../toolbelt/preferences.py \
    ../../toolbelt/range_slider.py \
    ../../toolbelt/translator.py

TRANSLATIONS = geotuileur_fr.ts
