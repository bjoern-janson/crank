from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Dict, Optional, Tuple
import time
from corrective_state import CanonicalAnomaly, CanonicalClaim, CanonicalCorrection, CorrectiveState

class Authority(Enum):
    CONSTITUTIONAL=3
    AXIOM=3
    EMPIRICAL=2
    PROSPECTIVE=1
class BufferInvariantError(ValueError): pass
class DuplicateIdentityError(BufferInvariantError): pass
class UnknownDependencyError(BufferInvariantError): pass
class UnauthorizedAuthorityError(BufferInvariantError): pass
class ProtectedAuthorityError(BufferInvariantError): pass
class UnknownObservationError(BufferInvariantError): pass
class InvalidWarrantError(BufferInvariantError): pass

@dataclass(frozen=True)
class AuthorizedReceipt:
    receipt_id: str
    tool_name: str
    input_args: str
    output_summary: str
    validates_claim_id: str
    _issuer_token: object = field(repr=False, compare=False, default=None)
class ReceiptAuthority:
    def __init__(self): self.__issuer_token=object()
    def authorize_success(self, receipt_id, tool_name, input_args, output_summary, validates_claim_id):
        return AuthorizedReceipt(receipt_id, tool_name, input_args, output_summary, validates_claim_id, self.__issuer_token)
    def verifies(self, receipt): return isinstance(receipt, AuthorizedReceipt) and receipt._issuer_token is self.__issuer_token

@dataclass(frozen=True)
class ClaimNode:
    id: str; content: str; authority: Authority; dependencies: Tuple[str,...]=(); invalidated_by: Tuple[str,...]=(); timestamp: float=field(default_factory=time.time, compare=False)
    @property
    def falsified(self): return bool(self.invalidated_by)
@dataclass(frozen=True)
class FailureObservation:
    id: str; tool_name: str; input_args: str; error_trace: str; related_claim_id: str; timestamp: float=field(default_factory=time.time, compare=False)
@dataclass(frozen=True)
class CorrectiveRecord:
    id: str; observation_id: str; target_claim_id: str; constraint_key: str; negative_invariant: str; rationale: str; timestamp: float=field(default_factory=time.time, compare=False)

class CorrigibleBuffer:
    def __init__(self, system_axiom: str, receipt_authority: Optional[ReceiptAuthority]=None):
        self._nodes: Dict[str,ClaimNode]={}; self._failure_observations={}; self._corrective_records={}; self._receipt_ids=set(); self._receipt_authority=receipt_authority
        self._insert('sys_root', system_axiom, Authority.CONSTITUTIONAL, ())
    @property
    def nodes(self): return MappingProxyType(self._nodes)
    def _insert(self, claim_id, content, authority, depends_on):
        if claim_id in self._nodes: raise DuplicateIdentityError(claim_id)
        deps=tuple(sorted(set(depends_on))); missing=set(deps)-self._nodes.keys()
        if missing: raise UnknownDependencyError(sorted(missing))
        invalid=set()
        for d in deps: invalid.update(self._nodes[d].invalidated_by)
        n=ClaimNode(claim_id, content, authority, deps, tuple(sorted(invalid))); self._nodes[claim_id]=n; return n
    def add_claim(self, claim_id, content, depends_on=None): return self._insert(claim_id,content,Authority.PROSPECTIVE,depends_on or ())
    def record_tool_failure(self, observation_id, related_claim_id, tool, args, error):
        if observation_id in self._failure_observations: raise DuplicateIdentityError(observation_id)
        if related_claim_id not in self._nodes: raise UnknownDependencyError(related_claim_id)
        o=FailureObservation(observation_id,tool,args,error,related_claim_id); self._failure_observations[observation_id]=o; return o
    def warrant_correction(self, correction_id, observation_id, target_claim_id, constraint_key, negative_invariant, rationale):
        if correction_id in self._corrective_records: raise DuplicateIdentityError(correction_id)
        if observation_id not in self._failure_observations: raise UnknownObservationError(observation_id)
        if target_claim_id not in self._nodes: raise UnknownDependencyError(target_claim_id)
        if self._nodes[target_claim_id].authority is Authority.CONSTITUTIONAL: raise ProtectedAuthorityError(target_claim_id)
        o=self._failure_observations[observation_id]
        if not self._related(target_claim_id,o.related_claim_id): raise InvalidWarrantError('unrelated')
        c=CorrectiveRecord(correction_id,observation_id,target_claim_id,constraint_key,negative_invariant,rationale); self._corrective_records[correction_id]=c
        self._invalidate(target_claim_id, correction_id); self._cascade(); return c
    def _invalidate(self, claim_id, corr_id): self._nodes[claim_id]=replace(self._nodes[claim_id], invalidated_by=tuple(sorted(set(self._nodes[claim_id].invalidated_by)|{corr_id})))
    def _related(self,target,anc):
        if target==anc: return True
        seen=set(); stack=list(self._nodes[target].dependencies)
        while stack:
            x=stack.pop()
            if x==anc:return True
            if x in seen:continue
            seen.add(x);stack.extend(self._nodes[x].dependencies)
        return False
    def _cascade(self):
        changed=True
        while changed:
            changed=False
            for cid,node in tuple(self._nodes.items()):
                inv=set(node.invalidated_by)
                for d in node.dependencies: inv.update(self._nodes[d].invalidated_by)
                merged=tuple(sorted(inv))
                if merged!=node.invalidated_by:self._nodes[cid]=replace(node,invalidated_by=merged);changed=True
    def record_tool_success(self, receipt):
        if self._receipt_authority is None or not self._receipt_authority.verifies(receipt):
            raise UnauthorizedAuthorityError('receipt not authorized by this buffer')
        if receipt.receipt_id in self._receipt_ids: raise DuplicateIdentityError(receipt.receipt_id)
        if receipt.validates_claim_id not in self._nodes: raise UnknownDependencyError(receipt.validates_claim_id)
        self._receipt_ids.add(receipt.receipt_id)
        self._nodes[receipt.validates_claim_id]=replace(self._nodes[receipt.validates_claim_id], authority=Authority.EMPIRICAL)
        return self._nodes[receipt.validates_claim_id]
    def export_corrective_state(self):
        claims=tuple(CanonicalClaim(n.id,n.content,n.authority.name,n.dependencies,n.invalidated_by) for n in self._nodes.values())
        active=tuple(sorted((c for c in claims if not c.invalidated_by),key=lambda c:c.id)); invalid=tuple(sorted((c for c in claims if c.invalidated_by),key=lambda c:c.id))
        anomalies=tuple(sorted((CanonicalAnomaly(o.id,o.tool_name,o.input_args,o.error_trace,o.related_claim_id) for o in self._failure_observations.values()),key=lambda x:x.id))
        corrections=tuple(sorted((CanonicalCorrection(c.id,c.observation_id,c.target_claim_id,c.constraint_key,c.negative_invariant,c.rationale) for c in self._corrective_records.values()),key=lambda x:x.id))
        return CorrectiveState(active,invalid,anomalies,corrections)
