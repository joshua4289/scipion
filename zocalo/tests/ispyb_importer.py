#!/usr/bin/python

from datetime import datetime
from math import ceil
import logging
#import greylog
from pathlib2 import Path


class ISPyBImporter:
    def __init__(self, db, db_connection, core, mx, beamline, extra_data_provider):
        self.db = db
        self.db_connection = db_connection
        self.core = core
        self.mx = mx
        self.beamline = beamline
        self.extra_data_provider = extra_data_provider

    def import_file(self, source_path, ispyb_path):
        cursor = self.db_connection.connect(self.db)
        visit_id = self.get_visit_id(cursor, self.beamline, source_path)
        if visit_id is None:
            logging.error('Visit not found in ISPyB so not recording this source path {}'.format(source_path))
        else:
            self.insert_collection(cursor, visit_id, source_path, ispyb_path)
        self.db_connection.disconnect()

    def insert_collection(self, cursor, visit_id, source_path, ispyb_path):
        params = self.mx.get_data_collection_group_params()
        params['parentid'] = visit_id

        group_id = self.mx.insert_data_collection_group(cursor, params.values())

        params = self.mx.get_data_collection_params()
        params['parentid'] = group_id
        params['visitid'] = visit_id
        params['starttime'] = self.formatted_current_date()
        params['endtime'] = self.formatted_current_date()
        params['imgdir'] = str(source_path.parent) + '/'
        params['file_template'] = source_path.name
        self.extra_data_provider.augment(params, source_path)

        no_images = self.extra_data_provider.number_of_images(source_path)
        snapshot_path = ispyb_path.with_name(source_path.name)
        params['xtal_snapshot1'] = self.snapshot_image(snapshot_path, 0.15, no_images)
        params['xtal_snapshot2'] = self.snapshot_image(snapshot_path, 0.50, no_images)
        params['xtal_snapshot3'] = self.snapshot_image(snapshot_path, 0.85, no_images)
        params['xtal_snapshot4'] = str(snapshot_path.with_suffix('')) + '_full.png'

        self.mx.insert_data_collection(cursor, params.values())

    @staticmethod
    def snapshot_image(snapshot_path, percentage_through_images, no_images):
        suffix = '.{}.png'.format(str(int(ceil(no_images * percentage_through_images))).zfill(3))
        return str(snapshot_path.with_suffix(suffix))

    @staticmethod
    def formatted_current_date():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def create_ispyb_path(other_path):
        parts = list(Path(other_path).parts)
        index_of_processed = parts.index('raw')
        ispyb_parts = parts[:index_of_processed] + ['.ispyb'] + parts[index_of_processed+1:]
        return Path(*ispyb_parts)

    def get_visit_id(self, cursor, beamline, source_path):
        forty_days = 60*24*40
        visits = self.core.retrieve_current_sessions(cursor, beamline, forty_days)
        cm_visits = self.core.retrieve_current_cm_sessions(cursor, beamline)

        all_visits = list([visit for tup in visits + cm_visits for visit in tup])
        visits_for_file = list([visit for visit in all_visits if visit in source_path.parts])

        logging.debug(
            'found visits {} for beamline {} and source path {}'.format(visits_for_file, beamline, source_path))
        if visits_for_file:
            return self.core.retrieve_visit_id(cursor, visits_for_file[0])
        return None
