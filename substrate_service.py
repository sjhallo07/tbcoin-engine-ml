# services/substrate_service.py
import asyncio
import json
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import logging
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException

@dataclass
class ContractArtifact:
    code_hash: str
    contract_id: str
    metadata: Dict[str, Any]
    wasm_path: str
    contract_path: str

@dataclass
class ContractCallResult:
    success: bool
    result: Optional[Any]
    events: List[Dict]
    gas_consumed: int
    storage_deposit: int
    error: Optional[str] = None

class SubstrateContractService:
    def __init__(self, rpc_url: str = "https://edge.test.honeycombprotocol.com"):
        self.rpc_url = rpc_url
        self.substrate = SubstrateInterface(url=rpc_url)
        self.logger = logging.getLogger(__name__)
        
    async def upload_contract(
        self,
        suri: str,
        manifest_path: Optional[str] = None,
        password: Optional[str] = None,
        storage_deposit_limit: Optional[int] = None,
        execute: bool = False
    ) -> ContractArtifact:
        """Upload contract binary to chain"""
        
        cmd = ["cargo", "contract", "upload"]
        
        if manifest_path:
            cmd.extend(["--manifest-path", manifest_path])
        
        if password:
            cmd.extend(["--password", password])
            
        if storage_deposit_limit:
            cmd.extend(["--storage-deposit-limit", str(storage_deposit_limit)])
            
        if execute:
            cmd.append("--execute")
            
        cmd.extend(["--suri", suri, "--url", self.rpc_url])
        
        try:
            result = await self._run_command(cmd)
            code_hash = self._extract_code_hash(result.stdout)
            
            return ContractArtifact(
                code_hash=code_hash,
                contract_id="",  # Will be set after instantiation
                metadata=self._parse_upload_result(result.stdout),
                wasm_path=self._find_wasm_file(manifest_path),
                contract_path=manifest_path
            )
            
        except Exception as e:
            self.logger.error(f"Contract upload failed: {e}")
            raise
    
    async def instantiate_contract(
        self,
        suri: str,
        constructor: str,
        args: List[str],
        code_hash: Optional[str] = None,
        manifest_path: Optional[str] = None,
        password: Optional[str] = None,
        storage_deposit_limit: Optional[int] = None,
        execute: bool = False
    ) -> ContractArtifact:
        """Instantiate a contract on chain"""
        
        cmd = ["cargo", "contract", "instantiate"]
        cmd.extend(["--constructor", constructor])
        cmd.extend(["--args"] + args)
        cmd.extend(["--suri", suri])
        
        if code_hash:
            cmd.extend(["--code-hash", code_hash])
            
        if manifest_path:
            cmd.extend(["--manifest-path", manifest_path])
            
        if password:
            cmd.extend(["--password", password])
            
        if storage_deposit_limit:
            cmd.extend(["--storage-deposit-limit", str(storage_deposit_limit)])
            
        if execute:
            cmd.append("--execute")
            
        cmd.extend(["--url", self.rpc_url])
        
        try:
            result = await self._run_command(cmd)
            contract_address = self._extract_contract_address(result.stdout)
            
            return ContractArtifact(
                code_hash=code_hash or self._extract_code_hash(result.stdout),
                contract_id=contract_address,
                metadata=self._parse_instantiate_result(result.stdout),
                wasm_path=self._find_wasm_file(manifest_path),
                contract_path=manifest_path
            )
            
        except Exception as e:
            self.logger.error(f"Contract instantiation failed: {e}")
            raise
    
    async def call_contract(
        self,
        contract_address: str,
        message: str,
        args: List[str],
        suri: str,
        manifest_path: Optional[str] = None,
        password: Optional[str] = None,
        storage_deposit_limit: Optional[int] = None,
        execute: bool = False
    ) -> ContractCallResult:
        """Call a contract message"""
        
        cmd = ["cargo", "contract", "call"]
        cmd.extend(["--contract", contract_address])
        cmd.extend(["--message", message])
        cmd.extend(["--args"] + args)
        cmd.extend(["--suri", suri])
        
        if manifest_path:
            cmd.extend(["--manifest-path", manifest_path])
            
        if password:
            cmd.extend(["--password", password])
            
        if storage_deposit_limit:
            cmd.extend(["--storage-deposit-limit", str(storage_deposit_limit)])
            
        if execute:
            cmd.append("--execute")
            
        cmd.extend(["--url", self.rpc_url])
        
        try:
            result = await self._run_command(cmd)
            return self._parse_call_result(result.stdout)
            
        except Exception as e:
            self.logger.error(f"Contract call failed: {e}")
            return ContractCallResult(
                success=False,
                result=None,
                events=[],
                gas_consumed=0,
                storage_deposit=0,
                error=str(e)
            )
    
    async def remove_contract(
        self,
        suri: str,
        code_hash: str,
        manifest_path: Optional[str] = None,
        password: Optional[str] = None,
        execute: bool = False
    ) -> bool:
        """Remove contract code from chain"""
        
        cmd = ["cargo", "contract", "remove"]
        cmd.extend(["--suri", suri])
        cmd.extend(["--code-hash", code_hash])
        
        if manifest_path:
            cmd.extend(["--manifest-path", manifest_path])
            
        if password:
            cmd.extend(["--password", password])
            
        if execute:
            cmd.append("--execute")
            
        cmd.extend(["--url", self.rpc_url])
        
        try:
            result = await self._run_command(cmd)
            return "successfully removed" in result.stdout.lower()
            
        except Exception as e:
            self.logger.error(f"Contract removal failed: {e}")
            return False
    
    async def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run shell command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Command failed: {stderr.decode()}")
            
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
    
    def _extract_code_hash(self, output: str) -> str:
        """Extract code hash from command output"""
        # Parse the output to find code hash
        lines = output.split('\n')
        for line in lines:
            if "Code hash:" in line:
                return line.split(":")[1].strip()
        raise ValueError("Code hash not found in output")
    
    def _extract_contract_address(self, output: str) -> str:
        """Extract contract address from command output"""
        lines = output.split('\n')
        for line in lines:
            if "Contract:" in line:
                return line.split(":")[1].strip()
        raise ValueError("Contract address not found in output")
    
    def _parse_call_result(self, output: str) -> ContractCallResult:
        """Parse contract call result"""
        # Implement parsing logic based on cargo-contract output format
        return ContractCallResult(
            success=True,
            result=None,  # Parse actual result
            events=[],    # Parse events
            gas_consumed=0,  # Parse gas consumed
            storage_deposit=0  # Parse storage deposit
        )
    
    def _find_wasm_file(self, manifest_path: Optional[str]) -> str:
        """Find the compiled WASM file"""
        # Implementation to locate .wasm file
        return "path/to/contract.wasm"
    
    def _parse_upload_result(self, output: str) -> Dict[str, Any]:
        """Parse upload result for metadata"""
        return {"raw_output": output}
    
    def _parse_instantiate_result(self, output: str) -> Dict[str, Any]:
        """Parse instantiate result for metadata"""
        return {"raw_output": output}