# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import os
import time
from typing import List, Optional, Union

from fastapi import Body, File, Form, UploadFile
from integrations.elasticsearch import OpeaElasticSearchDataprep
from integrations.milvus import OpeaMilvusDataprep
from integrations.neo4j_llamaindex import OpeaNeo4jLlamaIndexDataprep
from integrations.opensearch import OpeaOpenSearchDataprep
from integrations.pgvect import OpeaPgvectorDataprep
from integrations.pipecone import OpeaPineConeDataprep
from integrations.qdrant import OpeaQdrantDataprep
from integrations.redis import OpeaRedisDataprep
from integrations.redis_finance import OpeaRedisDataprepFinance
from integrations.vdms import OpeaVdmsDataprep
from opea_dataprep_loader import OpeaDataprepLoader

from comps import (
    CustomLogger,
    ServiceType,
    opea_microservices,
    register_microservice,
    register_statistics,
    statistics_dict,
)
from comps.dataprep.src.utils import create_upload_folder

logger = CustomLogger("opea_dataprep_microservice")
logflag = os.getenv("LOGFLAG", False)
upload_folder = "./uploaded_files/"

dataprep_component_name = os.getenv("DATAPREP_COMPONENT_NAME", "OPEA_DATAPREP_REDIS")
# Initialize OpeaComponentLoader
loader = OpeaDataprepLoader(
    dataprep_component_name,
    description=f"OPEA DATAPREP Component: {dataprep_component_name}",
)


@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/ingest",
    host="0.0.0.0",
    port=5000,
)
@register_statistics(names=["opea_service@dataprep"])
async def ingest_files(
    files: Optional[Union[UploadFile, List[UploadFile]]] = File(None),
    link_list: Optional[str] = Form(None),
    chunk_size: int = Form(1500),
    chunk_overlap: int = Form(100),
    process_table: bool = Form(False),
    table_strategy: str = Form("fast"),
    ingest_from_graphDB: bool = Form(False),
    index_name: Optional[str] = Form(None),
):
    start = time.time()

    if logflag:
        logger.info(f"[ ingest ] files:{files}")
        logger.info(f"[ ingest ] link_list:{link_list}")

    try:
        # Use the loader to invoke the component
        if dataprep_component_name == "OPEA_DATAPREP_REDIS":
            response = await loader.ingest_files(
                files,
                link_list,
                chunk_size,
                chunk_overlap,
                process_table,
                table_strategy,
                ingest_from_graphDB,
                index_name,
            )
        else:
            if index_name:
                logger.error(
                    'Error during dataprep ingest invocation: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
                )
                raise

            response = await loader.ingest_files(
                files, link_list, chunk_size, chunk_overlap, process_table, table_strategy, ingest_from_graphDB
            )

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ ingest ] Output generated: {response}")
        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep ingest invocation: {e}")
        raise


@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/get",
    host="0.0.0.0",
    port=5000,
)
@register_statistics(names=["opea_service@dataprep"])
async def get_files(index_name: str = Body(None, embed=True)):
    start = time.time()

    if logflag:
        logger.info("[ get ] start to get ingested files")

    try:
        # Use the loader to invoke the component
        if dataprep_component_name == "OPEA_DATAPREP_REDIS":
            response = await loader.get_files(index_name)
        else:
            if index_name:
                logger.error(
                    'Error during dataprep get files: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
                )
                raise
            response = await loader.get_files()

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ get ] ingested files: {response}")
        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep get invocation: {e}")
        raise


@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/delete",
    host="0.0.0.0",
    port=5000,
)
@register_statistics(names=["opea_service@dataprep"])
async def delete_files(file_path: str = Body(..., embed=True), index_name: str = Body(None, embed=True)):
    start = time.time()

    if logflag:
        logger.info("[ delete ] start to delete ingested files")

    try:
        # Use the loader to invoke the component
        if dataprep_component_name == "OPEA_DATAPREP_REDIS":
            response = await loader.delete_files(file_path, index_name)
        else:
            if index_name:
                logger.error(
                    'Error during dataprep delete files: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
                )
                raise
            response = await loader.delete_files(file_path)

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ delete ] deleted result: {response}")
        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)
        return response
    except Exception as e:
        logger.error(f"Error during dataprep delete invocation: {e}")
        raise


@register_microservice(
    name="opea_service@dataprep",
    service_type=ServiceType.DATAPREP,
    endpoint="/v1/dataprep/indices",
    host="0.0.0.0",
    port=5000,
)
@register_statistics(names=["opea_service@dataprep"])
async def get_list_of_indices():
    start = time.time()
    if logflag:
        logger.info("[ get ] start to get list of indices.")

    if dataprep_component_name != "OPEA_DATAPREP_REDIS":
        logger.error(
            'Error during dataprep - get list of indices: "index_name" option is supported if "DATAPREP_COMPONENT_NAME" environment variable is set to "OPEA_DATAPREP_REDIS". i.e: export DATAPREP_COMPONENT_NAME="OPEA_DATAPREP_REDIS"'
        )
        raise

    try:
        # Use the loader to invoke the component
        response = await loader.get_list_of_indices()

        # Log the result if logging is enabled
        if logflag:
            logger.info(f"[ get ] list of indices: {response}")

        # Record statistics
        statistics_dict["opea_service@dataprep"].append_latency(time.time() - start, None)

        return response
    except Exception as e:
        logger.error(f"Error during dataprep get list of indices: {e}")
        raise


if __name__ == "__main__":
    logger.info("OPEA Dataprep Microservice is starting...")
    create_upload_folder(upload_folder)
    opea_microservices["opea_service@dataprep"].start()
