import json, os, logging, copy

# Import all services
from services.validate_part_num_service import ValidatePartNumService
from services.change_transfer_qty_service import ChangeTransferQtyService
from services.change_to_whse_service import ChangeToWhseService
from services.change_to_bin_service import ChangeToBinService
from services.change_from_whse_service import ChangeFromWhseService
from services.change_from_bin_service import ChangeFromBinService
from services.master_inventory_bin_tests_service import MasterInventoryBinTestsService
from services.pre_commit_transfer_service import PreCommitTransferService
from services.commit_transfer_service import CommitTransferService
from services.api_get_inventory_transfer import SalesBuzzClient
from services.update_status_service import UpdateStatusService
from utils.sites import site_user_map


class InventoryTransfer:
    def __init__(self, api_client_service):
        self.api = api_client_service
        self.logger = logging.getLogger("InventoryTransfer")

        # Inject all API services
        self.validate_part_num = ValidatePartNumService(self.api)
        self.change_qty = ChangeTransferQtyService(self.api)
        self.change_to_whse = ChangeToWhseService(self.api)
        self.change_to_bin = ChangeToBinService(self.api)
        self.change_from_whse = ChangeFromWhseService(self.api)
        self.change_from_bin = ChangeFromBinService(self.api)
        self.master_tests = MasterInventoryBinTestsService(self.api)
        self.pre_commit = PreCommitTransferService(self.api)
        self.commit_transfer = CommitTransferService(self.api)
        self.salesbuzz = SalesBuzzClient()
        self.update_status = UpdateStatusService()

        self.data_path = os.path.join("data", "transfer_data.json")


    # //////////////////////////////////////////////////////////////////////

    def get_mapping_values(self, salesman_id):
        """
        Fetch mapping from API, handle errors, and extract specific fields.
        Returns a dict with cleaned values or None on failure.
        """
        try:
            response = self.salesbuzz.get_mapping(salesman_id)
            # print("Mapping response:", response)

            # Ensure response is valid
            if not isinstance(response, dict):
                raise ValueError("Invalid response format: expected a dictionary")

            # Extract values safely
            return {
                "mapping_id":   response.get("_id"),
                "from_whs":     response.get("fromWHS"),
                "from_bin":     response.get("fromBIN"),
                "to_whs":       response.get("toWHS"),
                "to_bin":       response.get("toBIN"),
                "sales_person": response.get("salesPerson")
            }

        except Exception as e:
            print(f"Error while fetching mapping for salesman_id {salesman_id}: {e}")
            return None


    def load_transfer_data(self):
        self.logger.info("=== STARTING INVENTORY TRANSFERS ===")

        try:
            response = self.salesbuzz.get_inventory_transfers()

            if not response:
                self.logger.warning("No transfers returned from SalesBuzz.")
                return []

            if not isinstance(response, dict):
                self.logger.error(f"Invalid response type: {type(response)}. Expected dict.")
                return []

            # Validate 'inventory' key exists and is a list
            if "inventory" not in response or not isinstance(response["inventory"], list):
                self.logger.error("Response missing 'inventory' list.")
                return []

            transfers = response["inventory"]
            count = response.get("count", len(transfers))

            self.logger.info(f"Fetched {count} transfers from SalesBuzz.")
            return transfers

        except Exception as e:
            self.logger.exception(f"❌ Failed to fetch transfers from SalesBuzz: {str(e)}")
            return []


    # ////////////////////////////////////////////////////////////////////

    def process_transfer(self, username, password, record):
        # print("\n--- Starting transfer:", record["TransferNo"], record)
        transfer_no = record["TransferNo"]
        parts = record.get("parts", [])
        trans_date= record.get("TranferDate", "")
        salesman_id= record.get("SalesmanNo", "") # to get salesManWarehouse 
        
        # here to get towhse frm whse and  bin from bin
        mapping_info = self.get_mapping_values(salesman_id)

        if mapping_info:
            from_whs     = mapping_info["from_whs"]
            from_bin     = mapping_info["from_bin"]
            to_whs       = mapping_info["to_whs"]
            to_bin       = mapping_info["to_bin"]
            sales_person = mapping_info["sales_person"]



        site= record.get("salesManWarehouse", "")

        for part in parts:  # Process only the first part for testing
            part_num = part["ItemNo"]
            qty = part["OriginalQty"]
            UOMID = part.get("UOMID", "")

            # 1. ValidatePartNum -----------------------------------------
            payload = {
                "proposedPartNum": part_num,
                "uomCodePartXRef": "",
                "refreshMode": False,
                "partList": "",
                "ds": {
                    "SNFormat": [],
                    "InvTrans": [],
                    "InvTransPartAlloc": [],
                    "LegalNumGenOpts": [],
                    "Parts": [],
                    "SelectedSerialNumbers": [],
                    "TransferHistory": []
                }
            }

            resp = self.validate_part_num.execute(username, password, payload)
            # print("Validate Part Num Response--------------------------------------------------", resp)
            invtrans_original = resp["data"]["returnObj"]["InvTrans"]
            # print("inv Transfer Original--------------------------------------------------", invtrans_original)

            # build modified InvTrans with RowMod
            invtrans_modified = []
            for item in invtrans_original:
                invtrans_modified.append(item)
                new_item = copy.deepcopy(item)
                new_item["RowMod"] = "U"
                # TranReference also needs to be updated
                new_item["TranReference"] = transfer_no
                # new_item["TranDate"] = trans_date
                invtrans_modified.append(new_item)
                # print("inv Transfer--------------------------------------------------", invtrans_modified)

            # 2. ChangeTransferQty ---------------------------------------
            qty_payload = {
                "proposedValue": qty,
                "ds": {
                    "InvTrans": invtrans_modified,
                    "TransferHistory": [],
                    "InvTransPartAlloc": [],
                    "LegalNumGenOpts": [],
                    "Parts": [],
                    "SelectedSerialNumbers": [],
                    "SNFormat": [],
                    "ExtensionTables": []
                }
            }
            res_qty = self.change_qty.execute(username, password, qty_payload)
            # print("Change Transfer Qty Response--------------------------------------------------", res_qty)
            ds = res_qty["data"]["parameters"]["ds"]

            # 3. ChangeToWhse --------------------------------------------
            res_whse = self.change_to_whse.execute(username, password, {
                "ipToWhse": to_whs ,   # Hardcoded for testing; replace with record["WarehouseID"] in production
                "ds": ds
            })
            ds = res_whse["data"]["parameters"]["ds"]

            # 4. ChangeToBin ---------------------------------------------
            res_bin = self.change_to_bin.execute(username, password, {
                "ipToBinNum": to_bin , 
                "ds": ds
            })
            ds = res_bin["data"]["parameters"]["ds"]

            # 5. ChangeFromWhse ------------------------------------------
            res_fwhse = self.change_from_whse.execute(username, password, {
                "ipwhseCode": from_whs,  # Hardcoded for testing; replace with record["FromWhse"] in production
                "ds": ds
            })
            ds = res_fwhse["data"]["parameters"]["ds"]

            # 6. ChangeFromBin -------------------------------------------
            res_fbin = self.change_from_bin.execute(username, password, {
                "ipBinNum": from_bin ,
                "ds": ds
            })
            ds = res_fbin["data"]["parameters"]["ds"]

            # 7. MasterInventoryBinTests --------------------------------
            res_master = self.master_tests.execute(username, password, {
                "ds": ds
            })
            ds = res_master["data"]["parameters"]["ds"]

            # 8. PreCommitTransfer --------------------------------------
            res_pre = self.pre_commit.execute(username, password, {
                "ds": ds
            })
            ds = res_pre["data"]["parameters"]["ds"]

            # 9. CommitTransfer -----------------------------------------
            res_commit = self.commit_transfer.execute(username, password, {
                "ds": ds
            })


            print("\n✔ TRANSFER COMPLETED:", res_commit["data"])

    def start_transfer_flow(self, default_password):

        records = self.load_transfer_data()

        if not records:
            self.logger.warning("No records to process. Exiting transfer flow.")
            return

        self.logger.info(f"Processing {len(records)} transfer records...")

        for record in records:
            site = record.get("salesManWarehouse")

            if not site:
                self.logger.error(f"Record missing `salesManWarehouse`: {record}")
                continue

            username = site_user_map.get(site)

            if not username:
                self.logger.error(f"No username mapped for site '{site}'. Skipping record.")
                continue

            self.logger.info(f"-> Starting transfer {record.get('TransferNo')} for site: {site} using user: {username}")

            try:
                self.process_transfer(username, default_password, record)
                self.logger.info(f"[OK] Finished transfer {record.get('TransferNo')}")
                self.update_status.update_status(record.get("TransferNo"), "completed")
            except Exception as e:
                self.logger.exception(
                    f"[NO] Transfer {record.get('TransferNo')} failed: {str(e)}"
                )
                self.update_status.update_status(transfer_no, "issue")



