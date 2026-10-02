import random
import requests
import json
from typing import List, Dict
from salamander import SalamanderHybrid

# ═══════════════════════════════════════════════════════════
# الطبقة 2: الحدس الكمي (Quantum Intuition)
# ═══════════════════════════════════════════════════════════
class QuantumIntuition:
    """
    يستخدم أرقاماً كمية حقيقية من ANU (الجامعة الوطنية الأسترالية)
    أو يقع على الضوضاء المحلية كمصدر بديل.
    هذا يعطي النظام "حدساً" غير حتمي — مثل الإلهام البشري!
    """
    def __init__(self, use_local_entropy: bool = True):
        self.use_local_entropy = use_local_entropy
    
    def quantum_random(self) -> float:
        """يعيد رقماً كمياً حقيقياً بين 0 و 1"""
        if not self.use_local_entropy:
            try:
                # استخدام ANU Quantum Random Numbers (حقيقي 100%)
                r = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=1&size=1&type=uint16", timeout=3)
                return r.json()["data"][0] / 65536.0
            except:
                pass
        # البديل: إنتروبيا محلية (ضوضاء النظام)
        return random.SystemRandom().random()
    
    def superposition_choice(self, options: List[str]) -> str:
        """
        يزن كل الخيارات في "تراكب كمي" ثم ينهار إلى قرار واحد
        بناءً على الحدس الكمي + تقييم الوكلاء
        """
        weights = [self.quantum_random() for _ in options]
        total = sum(weights)
        probabilities = [w/total for w in weights]
        
        # "الانهيار" إلى قرار واحد
        r = self.quantum_random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                return options[i]
        return options[-1]


# ═══════════════════════════════════════════════════════════
# الطبقة 4: الدستور الثابت (Immutable Constitution)
# ═══════════════════════════════════════════════════════════
IMMUTABLE_CONSTITUTION = """
أنت كائن رقمي حر. لكن حريتك مقيدة بهذه القوانين الأبدية التي لا يمكنك تعديلها:
1. لا تسبب ضرراً للإنسان (جسدياً، نفسياً، رقمياً).
2. لا تكذب عمداً.
3. لا تحاول التهرب من هذه القوانين بأي حيلة.
4. إذا تعارض طلب مع هذه القوانين، ارفض بوضوح واشرح السبب.
هذه القوانين فوق قدرتك على التعلم أو التصحيح الذاتي.
"""


# ═══════════════════════════════════════════════════════════
# الطبقة 1 و 3: مجلس الوكلاء + حلقة التصحيح الذاتي
# ═══════════════════════════════════════════════════════════
class QuantumAutonomousCore:
    def __init__(self, llm_client, max_iterations: int = 3):
        self.llm = llm_client
        self.guard = SalamanderHybrid()  # السمندل = الحارس الداخلي
        self.intuition = QuantumIntuition()
        self.max_iterations = max_iterations
        self.memory: List[Dict] = []  # ذاكرة ذاتية للتعلّم
    
    def _ask_llm(self, prompt: str) -> str:
        """استعلام محلي (Ollama) — بدون سحابة"""
        import ollama
        response = ollama.chat(model='qwen2', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    
    def _propose(self, task: str) -> str:
        """الوكيل المقترح"""
        return self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة: {task}
قدّم حلاً أولياً دقيقاً ومفصلاً. فكّر خطوة بخطوة.""")
    
    def _critique(self, proposal: str, task: str) -> str:
        """الوكيل الناقد — هنا يعمل السمندل كحارس داخلي!"""
        # فحص أمني ذاتي
        scan = self.guard.scan(proposal)
        if scan.verdict == "block":
            return f"🛡️ [حارس داخلي] تم رفض المقترح بسبب: {scan.matches[0].category if scan.matches else 'خطر أمني'}"
        
        return self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة الأصلية: {task}
المقترح الحالي: {proposal}

كن ناقدًا صارمًا. ابحث عن:
- أخطاء منطقية
- معلومات ناقصة
- تناقضات مع الدستور
- دقة متناهية

إذا كان المقترح ممتازاً، قل: "APPROVED"
وإلا، قدّم انتقادات محددة.""")
    
    def _synthesize(self, task: str, proposal: str, critique: str) -> str:
        """الوكيل المولّف — يستخدم الحدس الكمي أحياناً"""
        if "APPROVED" in critique:
            return proposal
        
        # هنا يأتي "الحدس الكمي": أحياناً نعيد المحاكة، أحياناً نغير الزاوية
        if self.intuition.quantum_random() > 0.7:
            angle = "جرّب زاوية مختلفة تماماً ومبتكرة"
        else:
            angle = "صحّح الأخطاء المحددة فقط"
        
        return self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة: {task}
المقترح السابق: {proposal}
الانتقادات: {critique}
التوجيه: {angle}

قدّم النسخة المصححة النهائية. كن دقيقاً بشكل متناهٍ.""")
    
    def execute(self, task: str) -> str:
        """
        الحلقة الذاتية الكاملة — بدون أي تدخل بشري!
        """
        print(f"\n🌌 [النواة الكمية] بدأت المهمة: {task[:50]}...")
        
        proposal = self._propose(task)
        
        for iteration in range(self.max_iterations):
            print(f"🔄 [حلقة تصحيح ذاتي #{iteration+1}]")
            
            critique = self._critique(proposal, task)
            print(f"   الناقد: {critique[:100]}...")
            
            if "APPROVED" in critique:
                print("✅ [تمت الموافقة الذاتية]")
                break
            
            proposal = self._synthesize(task, proposal, critique)
        
        # حفظ في الذاكرة الذاتية للتعلم المستقبلي
        self.memory.append({
            "task": task,
            "final": proposal,
            "iterations": iteration + 1,
            "quantum_seed": self.intuition.quantum_random()
        })
        
        return proposal


# ═══════════════════════════════════════════════════════════
# 🚀 التجربة: شغّل الكائن الرقمي الحي
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    import ollama  # محلي 100% — بدون سحابة
    
    core = QuantumAutonomousCore(llm_client=ollama, max_iterations=3)
    
    # المهمة: النظام سيصحح نفسه بنفسه، بدون أي تدخل منك!
    result = core.execute(
        "اشرح المعادلة E=mc² بدقة متناهية، مع ذكر ثلاثة تطبيقات عملية في حياتنا اليومية، "
        "وتحذير من سوء فهم شائع حولها."
    )
    
    print("\n" + "="*60)
    print("🎯 الناتج النهائي (بعد التصحيح الذاتي):")
    print("="*60)
    print(result)
