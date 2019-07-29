from ispyb_importer import ISPyBImporter
from mock import MagicMock, Mock

from ispyb.mxacquisition import MXAcquisition
from pathlib2 import Path
from datetime import datetime


def test_creates_data_collection_with_group():
    cursor = MagicMock()
    db_connection = MagicMock()
    db_connection.connect = Mock(return_value=cursor)
    core = MagicMock()
    beamline = 'b45'
    visit = 'cm12345'
    group_id = 'group id'
    visit_id = 55555

    core.retrieve_current_sessions = Mock(return_value=((visit, 'some-other-visit'),))
    core.retrieve_current_cm_sessions = Mock(return_value=((visit, 'some-other-other-visit'),))
    core.retrieve_visit_id = Mock(return_value=visit_id)
    mx = MagicMock()
    mx.insert_data_collection_group = Mock(return_value=group_id)
    mx.get_data_collection_group_params = Mock(return_value=MXAcquisition().get_data_collection_group_params())
    data_collection = MXAcquisition().get_data_collection_params()
    mx.get_data_collection_params = Mock(return_value=data_collection)

    extra_data_provider = MagicMock()
    extra_data_provider.number_of_images.return_value = 200

    source_path = Path('/dls/test/{}/raw/somedata.txrm'.format(visit))
    ispyb_path = Path('/dls/test/{}/.ispyb/rundirectory/somedata.txrm'.format(visit))

    importer = ISPyBImporter('prod', db_connection, core, mx, beamline, extra_data_provider)
    importer.import_file(source_path, ispyb_path)

    db_connection.connect.assert_called_with('prod')
    forty_days = 57600
    core.retrieve_current_sessions.assert_called_with(cursor, beamline, forty_days)
    core.retrieve_current_cm_sessions.assert_called_with(cursor, beamline)
    core.retrieve_visit_id.assert_called_with(cursor, visit)

    mx.get_data_collection_group_params.assert_called_with()

    params = MXAcquisition().get_data_collection_group_params()
    params['parentid'] = visit_id
    group = params.values()

    mx.insert_data_collection_group.assert_called_with(cursor, group)

    mx.get_data_collection_params.assert_called_with()

    params = MXAcquisition().get_data_collection_params()
    params['parentid'] = group_id
    params['visitid'] = visit_id
    params['starttime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['endtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['imgdir'] = '/dls/test/{}/raw/'.format(visit)
    params['file_template'] = 'somedata.txrm'
    params['xtal_snapshot1'] = '/dls/test/{}/.ispyb/rundirectory/somedata.030.png'.format(visit)
    params['xtal_snapshot2'] = '/dls/test/{}/.ispyb/rundirectory/somedata.100.png'.format(visit)
    params['xtal_snapshot3'] = '/dls/test/{}/.ispyb/rundirectory/somedata.170.png'.format(visit)
    params['xtal_snapshot4'] = '/dls/test/{}/.ispyb/rundirectory/somedata_full.png'.format(visit)

    collection = params.values()

    extra_data_provider.augment.assert_called_with(data_collection, source_path)
    mx.insert_data_collection.assert_called_with(cursor, collection)

    db_connection.disconnect.assert_called_with()
