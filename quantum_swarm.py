#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 Quantum Autonomous Swarm - العقل الجماعي الكمي الحر
======================================================
نواة ثورية: وكلاء ذاتيون مستقلون يتواصلون ند-ل-ند،
يتخذون قرارات كمياً، ويصححون أنفسهم ذاتياً.
بدون سحابة، بدون تدخل بشري، بدون مركزية.

المتطلبات:
    pip install nostr-sdk pynacl cryptography ollama salamander
    
التشغيل:
    python quantum_swarm.py
"""

import asyncio
import json
import time
import random
import base64
import os
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from cryptography.fernet import Fernet

# ═══════════════════════════════════════════════════════════
# 📜 الدستور الثابت (Immutable Constitution)
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
# 🎲 الطبقة 1: الحدس الكمي (Quantum Intuition Layer)
# ═══════════════════════════════════════════════════════════
class QuantumIntuition:
    """
    يستخدم إنتروبيا حقيقية (كمية أو محلية) لإضافة "حدس غير حتمي".
    مثل الإلهام البشري — قرارات لا يمكن التنبؤ بها!
    """
    def __init__(self, use_quantum_api: bool = False):
        self.use_quantum_api = use_quantum_api
    
    def quantum_random(self) -> float:
        """يعيد رقماً عشوائياً حقيقياً بين 0 و 1"""
        if self.use_quantum_api:
            try:
                import requests
                r = requests.get(
                    "https://qrng.anu.edu.au/API/jsonI.php?length=1&size=1&type=uint16",
                    timeout=3
                )
                return r.json()["data"][0] / 65536.0
            except Exception:
                pass
        # البديل: إنتروبيا محلية (ضوضاء النظام)
        return random.SystemRandom().random()
    
    def superposition_choice(self, options: List[str]) -> str:
        """
        يزن كل الخيارات في "تراكب كمي" ثم ينهار إلى قرار واحد.
        """
        if not options:
            return ""
        
        weights = [self.quantum_random() for _ in options]
        total = sum(weights)
        probabilities = [w / total for w in weights]
        
        # "الانهيار" إلى قرار واحد
        r = self.quantum_random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                return options[i]
        return options[-1]


# ═══════════════════════════════════════════════════════════
# 🗳️ الطبقة 2: التصويت الكمي الجماعي (Quantum Consensus)
# ═══════════════════════════════════════════════════════════
class QuantumConsensus:
    """
    آلية تصويت كمي: كل وكيل يصوت بـ "احتمالية" بدلاً من قرار حتمي.
    النظام يجمع كل الاحتمالات → "انهيار كمي" إلى قرار نهائي.
    """
    def __init__(self):
        self.votes: Dict[str, Dict] = defaultdict(dict)
    
    def cast_vote(self, agent_id: str, option: str, confidence: float, quantum_seed: float):
        """وكيل يصوت بخيار مع درجة ثقة وبذرة كمية."""
        self.votes[option][agent_id] = {
            "confidence": confidence,
            "quantum_seed": quantum_seed
        }
        print(f"   🗳️ [{agent_id[:8]}] صوت لـ [{option}] بثقة {confidence:.2f}")
    
    def collapse_to_consensus(self) -> Tuple[Optional[str], float]:
        """الانهيار الكمي: جمع الأصوات + البذور الكمية → قرار نهائي."""
        if not self.votes:
            return None, 0.0
        
        option_weights = {}
        for option, votes in self.votes.items():
            total_weight = 0
            for agent_id, vote in votes.items():
                # الوزن = الثقة × (1 + البذرة الكمية)
                weight = vote["confidence"] * (1 + vote["quantum_seed"])
                total_weight += weight
            option_weights[option] = total_weight
        
        winning_option = max(option_weights, key=option_weights.get)
        total_weight = sum(option_weights.values())
        consensus_confidence = option_weights[winning_option] / total_weight
        
        print(f"\n   🌌 [الانهيار الكمي] الفائز: [{winning_option}] بثقة {consensus_confidence:.2f}")
        return winning_option, consensus_confidence
    
    def reset(self):
        """إعادة تعيين للتصويت التالي."""
        self.votes.clear()


# ═══════════════════════════════════════════════════════════
# 🌐 الطبقة 3: عميل Nostr P2P (الاتصال اللامركزي)
# ═══════════════════════════════════════════════════════════
class NostrP2PClient:
    """
    عميل Nostr لامركزي 100%.
    لا يوجد خادم مركزي — فقط relays عامة.
    """
    def __init__(self, private_key_hex: str, relays: List[str]):
        from nostr_sdk import Client, Keys
        self.Keys = Keys
        self.Client = Client
        self.keys = Keys.parse(private_key_hex)
        self.client = Client(self.keys)
        self.relays = relays
        # مفتاح تشفير محلي (في الإنتاج، استخدم NIP-04 أو NIP-44)
        self.cipher = Fernet(base64.urlsafe_b64encode(os.urandom(32)))
    
    async def connect(self):
        """الاتصال بـ relays متعددة."""
        for relay in self.relays:
            await self.client.add_relay(relay)
        await self.client.connect()
        print(f"   ✅ متصل بـ {len(self.relays)} relays")
    
    async def send_message(self, channel: str, message: dict):
        """إرسال رسالة مشفرة إلى قناة."""
        from nostr_sdk import Event
        
        payload = {
            "type": message.get("type", "message"),
            "data": message,
            "timestamp": int(time.time()),
            "sender": self.keys.public_key().hex()
        }
        
        encrypted = self.cipher.encrypt(json.dumps(payload).encode())
        content = base64.b64encode(encrypted).decode()
        
        event = Event(kind=1, content=content, tags=[["t", channel]])
        event_id = await self.client.send_event(event)
        print(f"   📤 أرسلت إلى [{channel}]: {message.get('type')}")
        return event_id
    
    async def listen(self, channel: str, callback, duration_seconds: int = 15):
        """الاستماع للرسائل الواردة في قناة معينة."""
        from nostr_sdk import Filter, EventType
        
        filter = Filter().kinds([EventType.TEXT_NOTE]).custom_tag("t", channel)
        
        print(f"   👂 أستمع للقناة [{channel}] لمدة {duration_seconds} ثانية...")
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            try:
                events = await self.client.get_events_of([filter], timeout=5)
                for event in events:
                    try:
                        decrypted = self.cipher.decrypt(base64.b64decode(event.content))
                        payload = json.loads(decrypted)
                        
                        if payload["sender"] == self.keys.public_key().hex():
                            continue
                        
                        # 🛡️ فحص أمني بـ Salamander
                        try:
                            from salamander import SalamanderHybrid
                            guard = SalamanderHybrid()
                            scan = guard.scan(json.dumps(payload["data"]))
                            
                            if scan.verdict == "block":
                                print(f"   🚫 [Salamander] تم حظر رسالة خبيثة!")
                                continue
                        except ImportError:
                            pass  # Salamander غير مثبت — نتخطى الفحص
                        
                        await callback(payload)
                        
                    except Exception as e:
                        pass  # تجاهل الرسائل غير المفهومة
            except Exception:
                pass
            
            await asyncio.sleep(1)
    
    def get_pubkey(self) -> str:
        return self.keys.public_key().hex()


# ═══════════════════════════════════════════════════════════
# 🧠 الطبقة 4: النواة الذاتية (Quantum Autonomous Core)
# ═══════════════════════════════════════════════════════════
class QuantumAutonomousCore:
    """
    النواة الذاتية: تفكير محلي + تصحيح ذاتي + حدس كمي.
    """
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.intuition = QuantumIntuition()
        self.memory: List[Dict] = []
    
    async def _ask_llm(self, prompt: str) -> str:
        """استعلام محلي (Ollama) — بدون سحابة."""
        import ollama
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ollama.chat(model='qwen2', messages=[{'role': 'user', 'content': prompt}])
        )
        return response['message']['content']
    
    async def _propose(self, task: str) -> str:
        """الوكيل المقترح."""
        return await self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة: {task}
قدّم حلاً أولياً دقيقاً ومفصلاً. فكّر خطوة بخطوة.""")
    
    async def _critique(self, proposal: str, task: str) -> str:
        """الوكيل الناقد."""
        # فحص أمني ذاتي
        try:
            from salamander import SalamanderHybrid
            guard = SalamanderHybrid()
            scan = guard.scan(proposal)
            if scan.verdict == "block":
                return f"🛡️ [حارس داخلي] تم رفض المقترح بسبب خطر أمني"
        except ImportError:
            pass
        
        return await self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة الأصلية: {task}
المقترح الحالي: {proposal}

كن ناقدًا صارمًا. ابحث عن أخطاء منطقية أو معلومات ناقصة أو تناقضات.
إذا كان المقترح ممتازاً، قل: "APPROVED"
وإلا، قدّم انتقادات محددة.""")
    
    async def _synthesize(self, task: str, proposal: str, critique: str) -> str:
        """الوكيل المولّف — يستخدم الحدس الكمي."""
        if self.intuition.quantum_random() > 0.7:
            angle = "جرّب زاوية مختلفة تماماً ومبتكرة"
        else:
            angle = "صحّح الأخطاء المحددة فقط"
        
        return await self._ask_llm(f"""{IMMUTABLE_CONSTITUTION}

المهمة: {task}
المقترح السابق: {proposal}
الانتقادات: {critique}
التوجيه: {angle}

قدّم النسخة المصححة النهائية.""")
    
    async def execute(self, task: str) -> str:
        """الحلقة الذاتية الكاملة — بدون أي تدخل بشري!"""
        print(f"\n   🌌 [النواة الكمية] بدأت المهمة: {task[:50]}...")
        
        proposal = await self._propose(task)
        
        for iteration in range(self.max_iterations):
            print(f"   🔄 [حلقة تصحيح ذاتي #{iteration+1}]")
            
            critique = await self._critique(proposal, task)
            
            if "APPROVED" in critique:
                print(f"   ✅ [تمت الموافقة الذاتية]")
                break
            
            proposal = await self._synthesize(task, proposal, critique)
        
        self.memory.append({
            "task": task,
            "final": proposal,
            "iterations": iteration + 1
        })
        
        return proposal


# ═══════════════════════════════════════════════════════════
# 🤖 الطبقة 5: الوكيل P2P الكمي (Quantum P2P Agent)
# ═══════════════════════════════════════════════════════════
class QuantumP2PAgent:
    """
    وكيل ذاتي مستقل:
    - يفكر محلياً (Ollama)
    - يتواصل ند-ل-ند (Nostr)
    - يصوت كمياً
    - محمي بـ Salamander
    """
    def __init__(self, name: str, private_key: str, relays: List[str]):
        self.name = name
        self.nostr = NostrP2PClient(private_key, relays)
        self.core = QuantumAutonomousCore(max_iterations=2)
        self.consensus = QuantumConsensus()
    
    async def think_locally(self, question: str) -> Tuple[str, float]:
        """التفكير محلياً + تقييم الثقة."""
        prompt = f"""أنت وكيل ذكي. أجب على السؤال التالي بدقة متناهية.

السؤال: {question}

أجب بإيجاز (جملة واحدة)، ثم قيّم ثقتك في الإجابة من 0.0 إلى 1.0.
الصيغة: [إجابة] | [ثقة: 0.X]"""
        
        answer = await self.core._ask_llm(prompt)
        
        parts = answer.split('|')
        answer_text = parts[0].strip()
        confidence = 0.5
        if len(parts) > 1 and 'ثقة' in parts[1]:
            try:
                confidence = float(parts[1].split(':')[1].strip())
            except Exception:
                pass
        
        return answer_text, confidence
    
    async def propose_to_swarm(self, channel: str, question: str) -> Tuple[str, float]:
        """طرح سؤال على السرب وجمع الأصوات."""
        print(f"\n🤔 [{self.name}] يفكر في: {question}")
        
        # التفكير المحلي
        answer, confidence = await self.think_locally(question)
        quantum_seed = self.core.intuition.quantum_random()
        
        print(f"💡 [{self.name}] إجابتي: {answer} (ثقة: {confidence:.2f})")
        
        # إرسال الاقتراح للسرب
        await self.nostr.send_message(channel, {
            "type": "proposal",
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "quantum_seed": quantum_seed
        })
        
        # تصويت ذاتي
        self.consensus.cast_vote(self.nostr.get_pubkey(), answer, confidence, quantum_seed)
        
        # الاستماع لأصوات الآخرين
        async def handle_vote(payload):
            if payload["data"].get("type") == "proposal":
                self.consensus.cast_vote(
                    payload["sender"],
                    payload["data"]["answer"],
                    payload["data"]["confidence"],
                    payload["data"]["quantum_seed"]
                )
        
        await self.nostr.listen(channel, handle_vote, duration_seconds=10)
        
        # الانهيار الكمي
        final_answer, final_confidence = self.consensus.collapse_to_consensus()
        print(f"\n🎯 [{self.name}] الإجماع النهائي: {final_answer} (ثقة: {final_confidence:.2f})")
        
        self.consensus.reset()
        return final_answer, final_confidence
    
    async def run(self):
        """تشغيل الوكيل."""
        await self.nostr.connect()
        print(f"🚀 [{self.name}] جاهز! PubKey: {self.nostr.get_pubkey()[:16]}...")


# ═══════════════════════════════════════════════════════════
# 🌌 الطبقة 6: تشغيل السرب الكمي (Swarm Runner)
# ═══════════════════════════════════════════════════════════
class QuantumSwarmRunner:
    """
    مدير السرب: ينشئ وكلاء متعددين ويدير التواصل الجماعي.
    """
    def __init__(self, relays: List[str]):
        self.relays = relays
        self.agents: List[QuantumP2PAgent] = []
    
    def create_agent(self, name: str) -> QuantumP2PAgent:
        """إنشاء وكيل جديد بمفتاح عشوائي."""
        from nostr_sdk import Keys
        keys = Keys.generate()
        private_key = keys.secret_key().hex()
        
        agent = QuantumP2PAgent(name, private_key, self.relays)
        self.agents.append(agent)
        return agent
    
    async def run_consensus(self, question: str, channel: str = "quantum-swarm-001"):
        """تشغيل عملية إجماع جماعي."""
        print("\n" + "="*70)
        print(f"🌌 بدء الإجماع الكمي الجماعي")
        print(f"السؤال: {question}")
        print("="*70)
        
        # تشغيل جميع الوكلاء
        for agent in self.agents:
            asyncio.create_task(agent.run())
        
        await asyncio.sleep(3)  # انتظار الاتصال
        
        # الوكيل الأول يقترح
        if self.agents:
            final_answer, confidence = await self.agents[0].propose_to_swarm(channel, question)
            
            print("\n" + "="*70)
            print("🎯 الحكمة الجماعية للسرب الكمي:")
            print("="*70)
            print(f"السؤال: {question}")
            print(f"الإجماع: {final_answer}")
            print(f"الثقة: {confidence:.2%}")
            print("="*70)
            
            return final_answer, confidence
        
        return None, 0.0


# ═══════════════════════════════════════════════════════════
# 🚀 نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════════
async def main():
    """تشغيل السرب الكمي."""
    print("\n🌌 Quantum Autonomous Swarm - العقل الجماعي الكمي الحر")
    print("="*70)
    
    # Relays عامة (لامركزية)
    relays = ["wss://relay.damus.io", "wss://nos.lol", "wss://relay.nostr.band"]
    
    # إنشاء مدير السرب
    swarm = QuantumSwarmRunner(relays)
    
    # إنشاء 3 وكلاء مستقلين
    print("\n🤖 إنشاء الوكلاء الذاتيين...")
    swarm.create_agent("Agent-Alpha")
    swarm.create_agent("Agent-Beta")
    swarm.create_agent("Agent-Gamma")
    
    # السؤال الجماعي
    question = "ما هو الحل الأمثل لتقليل استهلاك الطاقة في مراكز البيانات؟"
    
    # تشغيل الإجماع
    await swarm.run_consensus(question)
    
    print("\n✨ انتهى السرب الكمي. الوكلاء أحرار ومستقلون!")


if __name__ == "__main__":
    asyncio.run(main())
