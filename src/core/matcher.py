import time
import json
import os
from typing import List, Dict, Tuple, Optional, Any
import torch
from sentence_transformers import SentenceTransformer, util


class GraphMatcher:
    def __init__(self,  model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def evaluate_candidate(self, cv_nouns: List[str], jd_skills: List[str], candidate_id: str) -> Tuple[float, Dict[str, Any], List[str]]:
        if not jd_skills or not cv_nouns: return 0.0, {}, []

        start_time = time.time()
        match_details = {}
        matched_nouns = set()
        
        # 1. Pre-encode once
        cv_noun_embs = self.model.encode(cv_nouns, convert_to_tensor=True)
        
        # Define strictness
        THRESHOLD = 0.6 

        for req_skill in jd_skills:
            skill_emb = self.model.encode(req_skill, convert_to_tensor=True)
            scores = util.cos_sim(skill_emb, cv_noun_embs)[0]
            
            best_idx = int(torch.argmax(scores))
            best_score = float(scores[best_idx])
            
            # --- THE SANITY CHECK ---
            # Calculate Reverse Similarity (Noun -> JD Skill)
            reverse_scores = util.cos_sim(cv_noun_embs[best_idx], skill_emb)
            reverse_score = float(reverse_scores[0][0])
            
            # Apply Symmetry Factor (Penalize one-way hallucinations)
            symmetry_factor = (best_score + reverse_score) / 2
            
            # Only count if it passes the threshold AND the symmetry factor is strong
            if best_score > THRESHOLD and symmetry_factor > (THRESHOLD - 0.1):
                best_noun = cv_nouns[best_idx]
                score_final = round(best_score * symmetry_factor, 2)
            else:
                best_noun = None
                score_final = 0.0
            
            match_details[req_skill] = {
                "score": score_final,
                "best_noun": best_noun,
                "method": "Symmetric_Cosine"
            }
            if best_noun: matched_nouns.add(best_noun)

        # 3. Finalization
        total_score = sum(d["score"] for d in match_details.values())
        final_percentage = round((total_score / len(jd_skills)) * 100, 2)
        
        metrics = {
            "score": final_percentage,
            "exec_time_ms": round((time.time() - start_time) * 1000, 2),
            "match_details": match_details
        }
        
        self._save_evaluation_progress(candidate_id, metrics)
        
        return final_percentage, match_details, list(matched_nouns)

    def _save_evaluation_progress(self, candidate_id: str, metrics: dict, filepath: str = "logs/metrics.json") -> None:
        """Appends evaluation metrics to a persistent log file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        log_entry = {
            "candidate_id": candidate_id, 
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), 
            "metrics": metrics
        }
        
        logs = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        logs.append(log_entry)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)